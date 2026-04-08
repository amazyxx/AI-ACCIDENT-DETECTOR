# 🚗 AI Accident Detection System

A real-time AI-powered accident detection system that uses computer vision to detect road accidents and send alerts.

---

## 📌 Features

- Real-time accident detection using YOLO
- Video upload support
- Web dashboard interface
- Alert system integration
- Fast processing

---

## 📁 Project Structure

```
ACCIDENT-SYSTEM/
├── templates/
│   └── index.html
├── uploads/
├── best.pt
├── detection.py
├── main.py
├── messaging.py
├── requirements.txt
```

---

## ⚙️ Installation

```bash
git clone https://github.com/amazyxx/accident-system.git
cd accident-system
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

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

- fastapi[all]
- numpy
- uvicorn
- ultralytics
- opencv-python
- twilio
- python-dotenv
- python-multipart

---

## 👤 Authors

1. Asma Mohamud Hashi  
https://github.com/asmamohamud652

2. Aziza Ibrahim Moahamed  
https://github.com/amazyxx

