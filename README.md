# 🚗 AI Accident Detection System

A real-time AI-powered accident detection system that uses computer vision to detect road accidents, manage live surveillance feeds, and dispatch automated Telegram alerts.

---

## 📌 Features

- **Real-Time Detection**: Utilizes a custom-trained YOLO model for high-accuracy accident identification.
- **Live Surveillance**: Integrated webcam support with a dedicated "Activate Live Cam" mode.
- **Dual-Source Analysis**: Seamlessly switch between live camera feeds and uploaded video files via a unified web dashboard.
- **Intelligent Alerting**: Sends snapshots to a dedicated folder and dispatches Telegram notifications using temporal logic to ensure accuracy.
- **Interactive Dashboard**: Modern web interface featuring a live video stream, real-time event logs, and an adjustable AI sensitivity slider.

---

## 📁 Project Structure

```text
ACCIDENT-SYSTEM/
├── alerts/             # 📸 Snapshots sent to Telegram (organized by timestamp)
├── templates/
│   ├── index.html      # Dashboard UI with unified system controls
│   └── history.html    # Archive of detected events
├── uploads/            # 📁 Stored video files for analysis
├── best.pt             # Trained YOLO model weights
├── detection.py        # Core vision logic & vehicle filtering
├── main.py             # FastAPI server & stream management
├── messaging.py        # Telegram Bot integration
└── requirements.txt    # Project dependencies
---

## ⚙️ Installation

# Clone the repository
git clone [https://github.com/amazyxx/accident-system.git](https://github.com/amazyxx/accident-system.git)
cd accident-system

# Set up virtual environment
python -m venv venv

# Activate venv (Mac/Linux)
source venv/bin/activate
# Activate venv (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

---

## ▶️ Usage

```bash
python main.py
```

Open in browser:
```
http://127.0.0.1:8000
```

---

## 🔍 How It Works

1. Upload video
2. Model processes frames
3. Detects accident
4. Sends alert
5. Displays result

---

## 📦 Requirements

Core AI and Computer Vision
- ultralytics
- opencv-python
- torch
- torchvision

Web Framework and Streaming
- fastapi[all]
- uvicorn[standard]
- jinja2
- python-multipart

Alerts and Utilities
- requests
- asyncio

