import numpy as np
import os
import cv2
from matplotlib import pyplot as plt
import pickle
import time
from pyfirmata import Arduino, util

DIGITAL_B = 11  # Blue LED
DIGITAL_G = 12  # Green LED
DIGITAL_R = 7   # Red LED
SERVO_PIN = 5
BUTTON_PIN = 10
WAIT_TIME = 2

flag = True

# === Setup Arduino ===
board = Arduino('/dev/tty.usbmodem1101')  # Replace with your port

# Start iterator for reading button input
it = util.Iterator(board)
it.start()
time.sleep(1)

# Setup pins
led_b = board.get_pin(f'd:{DIGITAL_B}:o')
led_g = board.get_pin(f'd:{DIGITAL_G}:o')
led_r = board.get_pin(f'd:{DIGITAL_R}:o')
servo = board.get_pin(f'd:{SERVO_PIN}:s')
button = board.get_pin(f'd:{BUTTON_PIN}:i')
button.enable_reporting()

# Initial LED state
led_b.write(1)


# === Take Picture with Webcam ===
camera = cv2.VideoCapture(0)
for i in range(3):
    success, img_captured = camera.read()
    time.sleep(0.3)
cv2.imwrite('capturedPicture.png', img_captured)
camera.release()

# === Load Models and Labels ===
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

with open("labels.pickle", "rb") as pickleFile:
    original_labels = pickle.load(pickleFile)
    labels = {v: k for k, v in original_labels.items()}

# === Process Captured Image ===
imagePath = 'capturedPicture.png'
image = cv2.imread(imagePath)
image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
plt.title("Original Image")
plt.imshow(image_RGB)
plt.xticks([]), plt.yticks([])
plt.show()

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
plt.title("Gray Image")
plt.imshow(gray, cmap='gray')
plt.xticks([]), plt.yticks([])
plt.show()

faces = faceCascade.detectMultiScale(
    gray,
    scaleFactor=1.21,
    minNeighbors=4,
    minSize=(20, 20),
    flags=cv2.CASCADE_SCALE_IMAGE
)
print(f'Faces found: {len(faces)}')

# === Face Recognition ===
confidence = 0
for (x, y, w, h) in faces:
    cv2.rectangle(image_RGB, (x, y), (x+w, y+h), (0, 255, 0), 5)
    roi_gray = gray[y:y+h, x:x+w]
    id_now, confidence = recognizer.predict(roi_gray)
    print("confidence =", confidence)
    # print("Face Recognized")
    # print("Access Granted")

plt.title("Faces Found")
plt.imshow(image_RGB)
plt.xticks([]), plt.yticks([])
plt.show()

# === Access Control Logic ===
if confidence >= 70 and len(faces) > 0:
    led_b.write(0)
    led_g.write(1)
    servo.write(180)
    time.sleep(1)
    servo.write(0)
    led_g.write(0)
    led_b.write(1)
    print("Access Granted")
    print("Opening the secret exit")
else:
    print("Access Denied")
    print("Security Breach")
    while flag:
        led_r.write(1)
        time.sleep(2)
        led_r.write(0)
        time.sleep(2)
        btn_value = button.read()
        if btn_value is True:  # button pressed
            print("System Reset")
            led_b.write(1)
            flag = False
            break

board.exit()
