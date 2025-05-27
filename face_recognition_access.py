
import numpy as np
import cv2
import pickle
import time
from datetime import datetime
from pyfirmata import Arduino, util
from matplotlib import pyplot as plt

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("cs131-final-project-49b00-firebase-adminsdk-fbsvc-f0f99ac33c.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cs131-final-project-49b00-default-rtdb.firebaseio.com/'
})

DIGITAL_B = 11
DIGITAL_G = 12
DIGITAL_R = 7
SERVO_PIN = 5
BUTTON_PIN = 10
SERVO_OPEN = 90
SERVO_CLOSED = 30

board = Arduino('/dev/tty.usbmodem1101')
it = util.Iterator(board)
it.start()
time.sleep(1)

led_b = board.get_pin(f'd:{DIGITAL_B}:o')
led_g = board.get_pin(f'd:{DIGITAL_G}:o')
led_r = board.get_pin(f'd:{DIGITAL_R}:o')
servo = board.get_pin(f'd:{SERVO_PIN}:s')
button = board.get_pin(f'd:{BUTTON_PIN}:i')
button.enable_reporting()

def reset_system_state():
    led_b.write(1)
    led_g.write(0)
    led_r.write(0)
    servo.write(SERVO_CLOSED)
    time.sleep(1)

reset_system_state()

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

with open("labels.pickle", "rb") as f:
    original_labels = pickle.load(f)
    labels = {v: k for k, v in original_labels.items()}

def recognize_face():
    camera = cv2.VideoCapture(0)
    for i in range(3):
        ret, img = camera.read()
        time.sleep(0.3)
    camera.release()

    if not ret:
        print("❌ Failed to capture image.")
        return

    cv2.imwrite('capturedPicture.png', img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faces = faceCascade.detectMultiScale(
        gray, scaleFactor=1.21, minNeighbors=4, minSize=(20, 20), flags=cv2.CASCADE_SCALE_IMAGE
    )

    print(f"Faces found: {len(faces)}")
    confidence = 0
    id_now = None

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        id_now, confidence = recognizer.predict(roi_gray)
        print("Confidence:", confidence)

        cv2.rectangle(image_RGB, (x, y), (x + w, y + h), (0, 255, 0), 2)
        name = labels.get(id_now, "Unknown")
        text = f"{name} (Confidence: {round(confidence, 2)})"
        cv2.putText(image_RGB, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    plt.title("Faces Found")
    plt.imshow(image_RGB)
    plt.xticks([]), plt.yticks([])
    plt.show()
    cv2.imwrite("annotated_result.png", cv2.cvtColor(image_RGB, cv2.COLOR_RGB2BGR))
    print("🖼 Annotated image saved as annotated_result.png")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref = db.reference("access_logs")

    if confidence >= 30 and len(faces) > 0:
        print("✅ Access Granted")
        ref.push({
            "status": "granted",
            "timestamp": timestamp,
            "person": labels.get(id_now, "Unknown"),
            "confidence": round(confidence, 2),
            "faces_found": len(faces)
        })
        led_b.write(0)
        led_g.write(1)
        servo.write(SERVO_OPEN)
        time.sleep(7)
    else:
        print("⛔ Access Denied")
        ref.push({
            "status": "denied",
            "timestamp": timestamp,
            "confidence": round(confidence, 2),
            "faces_found": len(faces)
        })
        led_b.write(0)
        led_r.write(1)
        time.sleep(7)

    reset_system_state()

print("🔄 System Ready. Press the button to attempt access.")

try:
    while True:
        if button.read() is True:
            print("🔘 Button Pressed")
            while button.read() is True:
                time.sleep(0.1)
            recognize_face()
            print("🟢 Ready for next attempt...")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("🛑 Exiting...")
    board.exit()
