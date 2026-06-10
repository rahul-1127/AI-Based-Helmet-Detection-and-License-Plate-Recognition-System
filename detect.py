import cv2
import os
from ultralytics import YOLO

# Load your trained model
# Adjusted path to point to backend/best.pt as we are running from root
model_path = "backend/best.pt"

# Load the input image
img_path = "backend/test.jpg"

if not os.path.exists(img_path):
    print(f"Error: Input image '{img_path}' not found. Please ensure 'test.jpg' exists in the 'backend' folder.")
    exit(1)

model = YOLO(model_path)

img = cv2.imread(img_path)

# Run detection
results = model(img, conf=0.1, iou=0.5, imgsz=640)[0]

# Get class names
names = results.names

# Loop through predictions
for box in results.boxes:
    cls = int(box.cls.item())
    label = names[cls]
    conf = float(box.conf.item())
    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

    # Choose color based on class
    if label == "WithHelmet":
        color = (0, 255, 0)    # Green
    elif label == "WithoutHelmet":
        color = (0, 0, 255)    # Red
    elif label == "Plate":
        color = (255, 0, 0)    # Blue
    else:
        color = (255, 255, 255)  # White default

    # Draw rectangle
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

    # Put label + confidence
    text = f"{label} {conf:.2f}"
    cv2.putText(img, text, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, color, 2)

# Save the output
output_path = "output_result.jpg"
cv2.imwrite(output_path, img)

print(f"Saved result with colored boxes at {output_path}")