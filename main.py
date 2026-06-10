#!/usr/bin/env python3
import cv2
import argparse
from ultralytics import YOLO
import numpy as np

# New imports for OCR and device management
from paddleocr import PaddleOCR
import torch
import time

# --- Configuration ---
MODEL_PATH = "backend/best.pt"


class YOLODetector:
    def __init__(self, path_of_model):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        self.model = YOLO(path_of_model)
        self.model.to(self.device)

        # Initialize PaddleOCR
        # The model is downloaded automatically when PaddleOCR is used for the first time
        print("Initializing PaddleOCR...")
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=torch.cuda.is_available())
        print("PaddleOCR initialized.")

        # Get class names and IDs from the model for robust matching
        self.class_names = self.model.names
        self.without_helmet_id = -1
        self.plate_id = -1
        for k, v in self.class_names.items():
            v_lower = v.lower()
            if 'without' in v_lower or 'no' in v_lower:
                self.without_helmet_id = k
            if 'plate' in v_lower:
                self.plate_id = k

        if self.without_helmet_id == -1:
            print("Warning: 'WithoutHelmet' or 'NoHelmet' class not found in model names.")
        if self.plate_id == -1:
            print("Warning: 'Plate' class not found in model names.")

    def predict_frame(self, frame):
        """
        Predicts objects in a single frame, performs OCR on license plates if a person without a helmet is detected.
        """
        original_image = frame.copy()

        # Predict and process results using the YOLO model
        results = self.model(original_image, verbose=False)
        result = results[0]

        detections = result.boxes
        plate_numbers = []

        # Check if any "WithoutHelmet" class is detected
        without_helmet_detected = any(int(box.cls[0]) == self.without_helmet_id for box in detections)

        # Store all detected plates if a person without a helmet is present
        plates_to_ocr = []
        if without_helmet_detected and self.plate_id != -1:
            for box in detections:
                if int(box.cls[0]) == self.plate_id:
                    plates_to_ocr.append(box.xyxy[0].cpu().numpy().astype(int))

        # Process all objects for drawing bounding boxes
        for box in detections:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = self.class_names[class_id]

            # Color selection
            label_lower = class_name.lower()
            if "without" in label_lower or "no" in label_lower:
                color = (0, 0, 255)    # Red
            elif "helmet" in label_lower:
                color = (0, 255, 0)    # Green
            elif "plate" in label_lower:
                color = (255, 0, 0)    # Blue
            else:
                color = (255, 255, 255) # White

            # Draw bounding box
            cv2.rectangle(original_image, (x1, y1), (x2, y2), color, 2)

            # Create label text
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(original_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Perform OCR on detected plates
        for (x1, y1, x2, y2) in plates_to_ocr:
            # Ensure bounding box is within image boundaries
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(original_image.shape[1], x2), min(original_image.shape[0], y2)

            # Crop the plate region
            plate_region = original_image[y1:y2, x1:x2]
            if plate_region.size == 0:
                continue

            # Apply OCR using PaddleOCR
            try:
                ocr_results = self.ocr.ocr(plate_region, cls=True)
                if ocr_results and ocr_results[0]:
                    # Concatenate text from all detected lines in the plate region
                    text = ''.join([line[1][0] for line in ocr_results[0]]).replace(" ", "")
                    plate_number = text.strip().upper()

                    # Simple filter for plate-like strings
                    if 6 <= len(plate_number) <= 10:
                        plate_numbers.append(plate_number)
                        print(f"OCR Extracted Plate: {plate_number}")
                        # Draw the OCR result on the image
                        cv2.putText(original_image, plate_number, (x1, y2 + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            except Exception as e:
                print(f"Error during OCR processing: {e}")

        return original_image, plate_numbers

    def process_image(self, image_path):
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Error: Could not read image from {image_path}")
            return

        annotated_frame, plate_numbers = self.predict_frame(frame)

        if plate_numbers:
            print("\nDetected License Plates:")
            for plate in set(plate_numbers):
                print(plate)

        cv2.imshow("Detection Result", annotated_frame)
        print("\nPress any key to exit.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def process_video(self, video_path):
        """
        Process a video file or webcam feed.
        """
        try:
            # Use 0 for webcam, or the path for a video file
            cap_source = 0 if video_path == 'webcam' else video_path
            cap = cv2.VideoCapture(cap_source)
            if not cap.isOpened():
                raise IOError(f"Cannot open source: {video_path}")
        except Exception as e:
            print(f"Error: {e}")
            return

        all_plate_numbers = set()

        # Variables for FPS calculation
        start_time = time.time()
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video stream or error reading frame.")
                break

            # FPS calculation starts
            frame_count += 1

            annotated_frame, plate_numbers = self.predict_frame(frame)
            if plate_numbers:
                all_plate_numbers.update(plate_numbers)

            # Calculate and display FPS on the frame
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                fps = frame_count / elapsed_time
                cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Real-time Helmet & Plate Detection", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if all_plate_numbers:
            print("\n--- All Unique License Plates Detected ---")
            for plate in all_plate_numbers:
                print(plate)
            print("----------------------------------------")


def main(source):
    """
    Main function to run detection on a given source.
    """
    # Load the YOLOv8 model and OCR
    try:
        detector = YOLODetector(MODEL_PATH)
    except Exception as e:
        print(f"Error initializing detector: {e}")
        print(f"Please ensure your model 'best.pt' is located at '{MODEL_PATH}'")
        print("And that you have installed all required packages (torch, paddleocr, etc.)")
        return

    # Check if the source is an image file
    if source.lower().endswith(('.png', '.jpg', '.jpeg')):
        detector.process_image(source)
    else:  # Assume video file or webcam
        detector.process_video(source)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helmet and License Plate Detection with OCR")
    parser.add_argument("--source", type=str, required=True, help="Path to image/video file or 'webcam' for live feed.")
    args = parser.parse_args()
    main(args.source)