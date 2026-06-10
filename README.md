# Helmet and License Plate Detection System

An AI-powered system that detects motorcyclists, distinguishes between those with and without helmets, identifies license plates, and performs OCR to extract plate numbers.

## Features
- **Helmet Detection**: Uses YOLOv8 to classify "WithHelmet" and "WithoutHelmet".
- **License Plate Extraction**: Detects "Plate" objects and performs OCR only when a violation (no helmet) is detected.
- **OCR Integration**: Utilizes PaddleOCR for robust text extraction from license plates.
- **Real-time Processing**: Supports image, video, and live webcam feeds.

## Project Structure
- `main.py`: The primary application script with OCR integration and device management.
- `detect.py`: A lightweight script for testing basic detection on single images.
- `app.py`: Entry point for the backend Flask service.
- `backend/`: Contains the trained YOLO model (`best.pt`) and backend logic.

## Installation

1. **Setup Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
`python main.py --source <path_to_image_or_video_or_webcam>`