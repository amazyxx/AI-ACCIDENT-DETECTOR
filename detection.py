import cv2
from ultralytics import YOLO

# Load model normally
model = YOLO('best.pt')

def detect_accidents(frame, conf_threshold=0.90):
    # Removed 'fuse=False' to fix the SyntaxError
    results = model.predict(frame, conf=conf_threshold, verbose=False)
    
    accident_detected = False
    h, w, _ = frame.shape

    # 📏 TRUCK FILTER: Making it even stricter.
    # If the box height is more than 30% of the screen, it's definitely a truck.
    max_allowed_height = h * 0.30 

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Get box dimensions
            coords = box.xyxy[0] 
            box_h = coords[3] - coords[1]

            # Your labels show class 6 is 'car_car' (accident)
            if class_id == 6:
                # 🛑 TRUCK BLOCKER:
                if box_h > max_allowed_height:
                    # This will print in your terminal so you can see it working
                    print(f"DEBUG: Blocked Truck (Height: {int(box_h)})")
                    continue
                
                # If it's a normal sized box and > 0.90 confidence, it's an accident
                accident_detected = True
        
        annotated_frame = r.plot()
        
    return annotated_frame, accident_detected