import os
import cv2
import time
import json
import shutil
import asyncio
import threading
from datetime import datetime
from fastapi import FastAPI, Request, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ultralytics import YOLO
from detection import detect_accidents
from messaging import AlertService

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# Load our trained model
model = YOLO('best.pt')
notifier = AlertService()

# --- UTILITY FUNCTIONS ---

def log_accident(class_name, confidence):
    """Saves accident data to history.json with newest entries at the top."""
    log_file = "history.json"
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": "Accident Detected",
        "class": class_name,
        "confidence": f"{confidence * 100:.1f}%"
    }
    
    data = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                data = json.load(f)
        except:
            data = []
    
    data.insert(0, log_entry)
    with open(log_file, "w") as f:
        json.dump(data[:50], f, indent=4)
    print(f"✅ History Updated: {log_entry['timestamp']}")

class ConnectionManager:
    """Manages WebSocket connections for real-time UI updates."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- GLOBAL STATE ---
CURRENT_VIDEO_PATH = None 
USE_WEBCAM = False
alert_sent = False
GLOBAL_CONFIDENCE = 0.75  # Set to 0.75 based on Precision-Confidence curves

# --- ROUTES ---

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    global CURRENT_VIDEO_PATH, USE_WEBCAM, alert_sent 
    
    # CRITICAL: Kill webcam mode so the loop switches to file
    USE_WEBCAM = False 

    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    CURRENT_VIDEO_PATH = file_path
    alert_sent = False 
    print(f"--- NEW VIDEO UPLOADED: {file.filename} ---")
    
    return RedirectResponse(url="/", status_code=303)

@app.get('/start_webcam')
async def start_webcam():
    global CURRENT_VIDEO_PATH, USE_WEBCAM, alert_sent
    CURRENT_VIDEO_PATH = None
    USE_WEBCAM = True
    alert_sent = False
    print("Live Feed Requested.")
    return RedirectResponse(url="/", status_code=303)

@app.get('/stop_stream')
async def stop_stream():
    global CURRENT_VIDEO_PATH, USE_WEBCAM, alert_sent
    CURRENT_VIDEO_PATH = None
    USE_WEBCAM = False
    alert_sent = False
    print("System Reset. All feeds stopped.")
    return RedirectResponse(url="/", status_code=303)

@app.get("/set_confidence")
async def set_confidence(value: float):
    global GLOBAL_CONFIDENCE
    GLOBAL_CONFIDENCE = value
    return {"status": "success", "value": GLOBAL_CONFIDENCE}

@app.get("/history", response_class=HTMLResponse)
async def get_history(request: Request):
    logs = []
    if os.path.exists("history.json"):
        with open("history.json", "r") as f:
            logs = json.load(f)
    return templates.TemplateResponse("history.html", {"request": request, "logs": logs})


# --- CORE PROCESSING ENGINE ---
def gen_frames():
    global CURRENT_VIDEO_PATH, USE_WEBCAM, alert_sent, GLOBAL_CONFIDENCE

    while True:
        # Idle check
        if not USE_WEBCAM and CURRENT_VIDEO_PATH is None:
            time.sleep(0.5)
            continue

        # Pick the source
        source = 0 if USE_WEBCAM else CURRENT_VIDEO_PATH
        cap = cv2.VideoCapture(source)
        
        consecutive_accident_frames = 0 
        prev_time = 0

        # Video Metadata for Speed Sync
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 30
        time_per_frame = 1.0 / fps

        while cap.isOpened():
            # THE SWITCH: This allows you to stop the webcam or upload a new video
            if USE_WEBCAM and source != 0: break 
            if not USE_WEBCAM and source == 0: break

            # Timing control
            time_elapsed = time.time() - prev_time
            if time_elapsed < time_per_frame:
                time.sleep(time_per_frame - time_elapsed)
            prev_time = time.time()

            success, frame = cap.read()
            if not success:
                break

            # Detection
            annotated_frame, accident_found = detect_accidents(frame, conf_threshold=GLOBAL_CONFIDENCE)
            
            # Telegram Logic
            if accident_found:
                consecutive_accident_frames += 1
                
                # Exactly 2 frames = 1 alert. No mess.
                if consecutive_accident_frames == 2: 
                    print("🚀 TRIGGERING TELEGRAM ALERT...")
                    
                    # Create the folder if it doesn't exist
                    os.makedirs("alerts", exist_ok=True)
                    
                    # Point the 'snap' variable to the new folder
                    snap = f"alerts/accident_{int(time.time())}.jpg"
                    
                    # Save the image into that folder
                    cv2.imwrite(snap, annotated_frame)
                    
                    msg = "🚨 ACCIDENT DETECTED!"
                    notifier.send_alert(msg, snap)
            else:
                consecutive_accident_frames = 0

            # Output to Browser
            ret, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if not ret:
                continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        cap.release()
        
        # Cleanup when video ends
        if not USE_WEBCAM:
            CURRENT_VIDEO_PATH = None
            print("--- VIDEO ENDED ---")
            break 
        else:
            time.sleep(0.1)

# --- WEB SERVERS ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get('/video_feed')
async def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
