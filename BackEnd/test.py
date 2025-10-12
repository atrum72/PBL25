# attendance.py
import os
import pickle
import face_recognition
import numpy as np
import pandas as pd
from datetime import datetime
import cv2  # for camera capture

# ---------- Paths ----------
BASE_DIR = os.path.dirname(__file__)
ENC_FILE = os.path.join(BASE_DIR, "encodings.pkl")
OUTPUT_DIR = os.path.join(BASE_DIR, "attendance")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- Load known encodings ----------
with open(ENC_FILE, "rb") as f:
    data = pickle.load(f)
known_encs = data["encodings"]
known_names = data["names"]

# ---------- Function to process any image ----------
def process_image(image):
    locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, locations)
    present_students = set()

    THRESHOLD = 0.5
    for enc in encodings:
        distances = face_recognition.face_distance(known_encs, enc)
        best_idx = np.argmin(distances)
        if distances[best_idx] < THRESHOLD:
            present_students.add(known_names[best_idx])
    return present_students

# ---------- Option 1: Process uploaded image ----------
def attendance_from_uploaded_image(image_path):
    img = face_recognition.load_image_file(image_path)
    present_students = process_image(img)
    save_attendance_report(present_students)

# ---------- Option 2: Process live camera ----------
def attendance_from_camera():
    video_capture = cv2.VideoCapture(0)
    input("Press Enter when ready to capture attendance from camera...")

    ret, frame = video_capture.read()
    video_capture.release()

    if not ret:
        print("Failed to capture from camera")
        return

    # Convert BGR -> RGB
    rgb_frame = frame[:, :, ::-1]
    present_students = process_image(rgb_frame)
    save_attendance_report(present_students)

# ---------- Save attendance ----------
def save_attendance_report(present_students):
    all_students = sorted(set(known_names))
    report = [{"Name": s, "Status": "Present" if s in present_students else "Absent"} for s in all_students]

    df = pd.DataFrame(report)
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(OUTPUT_DIR, f"attendance_{today_str}.xlsx")
    df.to_excel(output_file, index=False)
    print(f"Attendance saved to {output_file}")

# ---------- Example usage ----------
if __name__ == "__main__":
    choice = input("Use uploaded image or camera? (upload/camera): ").lower()
    if choice == "upload":
        path = input("Enter path to image: ")
        attendance_from_uploaded_image(path)
    elif choice == "camera":
        attendance_from_camera()
    else:
        print("Invalid choice")