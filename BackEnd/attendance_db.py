import os
import pickle
import face_recognition
import numpy as np
import mysql.connector
from datetime import date

# ---------- Paths ----------
BASE_DIR = os.path.dirname(__file__)
ENC_FILE = os.path.join(BASE_DIR, "encodings.pkl")

# ---------- Load encodings ----------
with open(ENC_FILE, "rb") as f:
    data = pickle.load(f)
known_encs = data["encodings"]
known_names = data["names"]

def mark_face_attendance(db, timetable_id, image_path=None, use_camera=False):
    if use_camera:
        # We must import cv2 here since 'use_camera=True' isn't called by the web app.
        # This is okay, as this branch isn't being run.
        import cv2 
        cap = cv2.VideoCapture(0)
        input("Press Enter to capture...")
        ret, frame = cap.read()
        cap.release()
        if not ret:
            print("Failed to capture from camera")
            return
        rgb_frame = frame[:, :, ::-1]
    
    # --- THIS IS THE MODIFIED BLOCK ---
    else:
        # 1. Load the image using the face_recognition library
        img = face_recognition.load_image_file(image_path)

        # 2. Check if it has an alpha channel (4 channels, e.g., PNG)
        if img.shape[2] == 4:
            # 3. Convert from RGBA to RGB by slicing off the 4th channel
            img = img[:, :, :3]
        
        # 4. Now 'img' is guaranteed to be a 3-channel RGB, 
        #    which is what the face_recognition functions expect.
        rgb_frame = img
    # --- END OF MODIFIED BLOCK ---

    # ---------- Process ----------
    locations = face_recognition.face_locations(rgb_frame)
    encodings = face_recognition.face_encodings(rgb_frame, locations)
    present_students = set()

    THRESHOLD = 0.5
    for enc in encodings:
        distances = face_recognition.face_distance(known_encs, enc)
        best_idx = np.argmin(distances)
        if distances[best_idx] < THRESHOLD:
            present_students.add(known_names[best_idx])

    # ---------- Update DB ----------
    today = date.today()
    cursor = db.cursor()
    for name in present_students:
        cursor.execute("SELECT student_id FROM students WHERE name=%s", (name,))
        res = cursor.fetchone()
        if res:
            # Assumes your 'db' connection uses a default tuple cursor
            student_id = res[0] 
            cursor.execute("""
                UPDATE attendance
                SET face_verified=TRUE
                WHERE student_id=%s AND timetable_id=%s AND date=%s
            """, (student_id, timetable_id, today))
    db.commit()
    
    # This print will go to your terminal
    print(f"[+] Face recognition attendance updated for {len(present_students)} students")
    
    # --- ADDED RETURN VALUE ---
    # This sends a message back to app.py, which sends it to the user.
    if len(present_students) == 0:
        raise Exception("No known students were recognized in the photo.")
    else:
        # This is the message the user will see.
        return f"Scan complete! {len(present_students)} student(s) marked."