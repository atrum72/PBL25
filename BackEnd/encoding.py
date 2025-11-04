# encode_faces.py
import os
import pickle
import face_recognition

# ---------- Config ----------
# Use path relative to this script file
DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset")
ENC_FILE = os.path.join(os.path.dirname(__file__), "encodings.pkl")

# ---------- Initialize ----------
encodings = []
names = []

# ---------- Loop through dataset ----------
for student in os.listdir(DATASET_DIR):
    student_folder = os.path.join(DATASET_DIR, student)
    if not os.path.isdir(student_folder):
        continue

    for img_file in os.listdir(student_folder):
        img_path = os.path.join(student_folder, img_file)
        try:
            # Load image
            img = face_recognition.load_image_file(img_path)
            # Detect faces
            boxes = face_recognition.face_locations(img)
            if not boxes:
                print(f"WARNING: No face found in {img_path}")
                continue
            # Get encoding (128-d vector)
            enc = face_recognition.face_encodings(img, boxes)[0]
            encodings.append(enc)
            names.append(student)
            print(f"Encoded: {img_path}")
        except Exception as e:
            print(f"ERROR processing {img_path}: {e}")

# ---------- Save encodings ----------
with open(ENC_FILE, "wb") as f:
    pickle.dump({"encodings": encodings, "names": names}, f)

print(f"\nDone! Encoded {len(encodings)} faces. Saved to {ENC_FILE}")