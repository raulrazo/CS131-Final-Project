import cv2
import os
import time

# === CONFIGURATION ===
person_name = "Raul"  # <-- Change this to your label
save_dir = os.path.join("faces", person_name)
os.makedirs(save_dir, exist_ok=True)

# === LOAD HAAR CASCADE FOR FACE DETECTION ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# === USE USB CAMERA (index 1) ===
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Could not open USB webcam. Try changing the index (1 → 2, etc.)")
    exit()

count = 0
max_images = 50  # Number of face images to capture

print("[INFO] Starting face capture. Follow on-screen instructions. Press 'q' to quit early.")

while count < max_images:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    # Show instruction text on screen
    instruction = f"Move your face slightly... Capturing image {count+1}/{max_images}"
    cv2.putText(frame, instruction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Draw rectangles around detected faces and save cropped face
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        face = gray[y:y+h, x:x+w]
        img_path = os.path.join(save_dir, f"{count}.jpg")
        cv2.imwrite(img_path, face)
        print(f"[INFO] Saved image {count+1} → {img_path}")
        count += 1
        time.sleep(0.5)  # 0.5 second delay between captures
        break  # Save only one face per frame

    cv2.imshow("Face Capture", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[INFO] Capture manually stopped.")
        break

cap.release()
cv2.destroyAllWindows()
print("[INFO] Capture complete.")
