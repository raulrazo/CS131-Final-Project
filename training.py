import os
import face_recognition
import pickle

base_dir = "faces"
known_encodings = []
known_labels = []

for person_name in os.listdir(base_dir):
    person_dir = os.path.join(base_dir, person_name)
    if not os.path.isdir(person_dir):
        continue

    for file in os.listdir(person_dir):
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            image_path = os.path.join(person_dir, file)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                known_labels.append(person_name)
                print(f"Encoded {file} as {person_name}")

with open("encodings.pickle", "wb") as f:
    pickle.dump({"encodings": known_encodings, "labels": known_labels}, f)

print("All encodings saved.")

