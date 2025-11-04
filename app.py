# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import hashlib
import os
import subprocess

# -------------------- APP SETUP --------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'supersecretkey'

# --- NEW: Define a folder for temporary scan uploads ---
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create the folder if it doesn't exist

# -------------------- DATABASE CONFIG --------------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Update with your MySQL username
app.config['MYSQL_PASSWORD'] = 'sanju'  # Update with your MySQL password
app.config['MYSQL_DB'] = 'attendify'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# -------------------- LOGIN --------------------
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor = mysql.connection.cursor()

    # Check student
    cursor.execute('SELECT * FROM students WHERE email=%s AND password=%s', (email, hashed_password))
    student = cursor.fetchone()
    if student:
        session['loggedin'] = True
        session['id'] = student['student_id']
        session['name'] = student['name']
        session['role'] = 'student'
        cursor.close()
        return redirect(url_for('student_dashboard'))

    # Check teacher
    cursor.execute('SELECT * FROM teachers WHERE email=%s AND password=%s', (email, hashed_password))
    teacher = cursor.fetchone()
    if teacher:
        session['loggedin'] = True
        session['id'] = teacher['teacher_id']
        session['name'] = teacher['name']
        session['role'] = 'teacher'
        cursor.close()
        return redirect(url_for('teacher_dashboard'))

    cursor.close()
    flash('Incorrect email or password!', 'danger')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# -------------------- REGISTRATION --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        college_id = request.form['college_id']
        department = request.form['department']
        email = request.form['email']
        profile_pic = request.files['profile_pic']
        face_photos = request.files.getlist('face_photos')

        # Hash a default password
        default_password = "pass@123"
        hashed_password = hashlib.sha256(default_password.encode()).hexdigest()

        # Save profile picture
        profile_folder = os.path.join(app.static_folder, 'uploads')
        os.makedirs(profile_folder, exist_ok=True)
        profile_path = os.path.join(profile_folder, profile_pic.filename)
        profile_pic.save(profile_path)

        # Save face recognition photos
        face_folder = os.path.join(app.static_folder, 'face_data', college_id)
        os.makedirs(face_folder, exist_ok=True)
        for photo in face_photos:
            photo.save(os.path.join(face_folder, photo.filename))

        # Insert student into database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO students (roll_no, name, department, email, password, face_image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (college_id, name, department, email, hashed_password, profile_path))
        mysql.connection.commit()
        cursor.close()

        flash("Registration successful! You can now login.", "success")
        return redirect(url_for('home'))

    return render_template('register.html')

# -------------------- DASHBOARDS --------------------
@app.route('/student_dashboard')
def student_dashboard():
    if 'loggedin' in session and session.get('role') == 'student':
        return render_template('student_dashboard.html', user_name=session.get('name'))
    return redirect(url_for('home'))

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'loggedin' in session and session.get('role') == 'teacher':
        teacher_id = session.get('id')
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT subject_name 
            FROM timetable 
            WHERE teacher_id = %s
            ORDER BY subject_name
        """, (teacher_id,))
        subjects_from_db = cursor.fetchall()
        cursor.close()
        teacher_subjects = [s['subject_name'] for s in subjects_from_db]
        return render_template('teacher_dashboard.html', user_name=session.get('name'), subjects=teacher_subjects)
    return redirect(url_for('home'))

# -------------------- FACE ATTENDANCE --------------------
@app.route('/api/scan-face', methods=['POST'])
def api_scan_face():
    if 'loggedin' not in session or session.get('role') != 'teacher':
        return jsonify({'status': 'error', 'message': 'Not authorized'}), 401

    if 'faceImage' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image file provided'}), 400

    file = request.files['faceImage']
    subject_name = request.form.get('subject') # Get subject name from JavaScript

    if file.filename == '' or not subject_name:
        return jsonify({'status': 'error', 'message': 'No image or subject selected'}), 400

    image_path = "" # Define here to be accessible in 'finally'
    try:
        # 1. Get teacher_id from session
        teacher_id = session.get('id')

        # 2. Find the timetable_id from the subject name and teacher
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT timetable_id FROM timetable 
            WHERE teacher_id = %s AND subject_name = %s
            LIMIT 1 
        """, (teacher_id, subject_name))
        timetable_entry = cursor.fetchone()
        cursor.close()

        if not timetable_entry:
            return jsonify({'status': 'error', 'message': f'Could not find timetable for {subject_name}'}), 404

        timetable_id = timetable_entry['timetable_id']

        # 3. Save the file temporarily
        filename = f"scan_{session['id']}_{timetable_id}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(image_path)

        # 4. Run your existing face scan function
        # We assume this function updates the DB and throws an error if it fails
        # attendance_db.mark_face_attendance(mysql.connection, timetable_id, image_path=image_path)
        # TODO: Call your actual face attendance function here
        print(f"Face scan for {timetable_id} with image {image_path} would run here.")
        
        # 5. If it succeeds, create a success message
        scan_result_message = "Face Scan complete. Attendance marked."

        return jsonify({
            'status': 'success', 
            'message': scan_result_message
        })

    except Exception as e:
        print(f"Error during scan: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
        
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

# -------------------- ATTENDANCE REPORT --------------------
@app.route('/attendance_report')
def attendance_report():
    if 'loggedin' not in session or session.get('role') != 'teacher':
        return redirect(url_for('home'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT s.name AS Student, t.subject_name, COUNT(*) AS Total_Classes,
        SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS Classes_Present,
        ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)/COUNT(*)*100,2) AS Attendance_Percentage
        FROM attendance a
        JOIN students s ON a.student_id=s.student_id
        JOIN timetable t ON a.timetable_id=t.timetable_id
        GROUP BY s.student_id, t.subject_name
        ORDER BY s.name, t.subject_name
    """)
    data = cursor.fetchall()
    cursor.close()
    return render_template('attendance_report.html', data=data)

# -------------------- API ENDPOINTS --------------------
@app.route('/api/students_for_subject/<subject_name>')
def get_students_for_subject(subject_name):
    if 'loggedin' in session and session.get('role') == 'teacher':
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT s.student_id, s.name, s.roll_no
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            JOIN timetable t ON a.timetable_id = t.timetable_id
            WHERE t.subject_name = %s
            ORDER BY s.roll_no
        """, (subject_name,))
        students = cursor.fetchall()
        cursor.close()
        return jsonify(students)
    return jsonify({"error": "Unauthorized"}), 401

@app.route('/api/teacher_subjects/<class_year>')
def get_teacher_subjects_by_year(class_year):
    if 'loggedin' in session and session.get('role') == 'teacher':
        teacher_id = session.get('id')
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT subject_name 
            FROM timetable 
            WHERE teacher_id = %s AND class_year = %s
            ORDER BY subject_name
        """, (teacher_id, class_year))
        subjects = cursor.fetchall()
        cursor.close()
        return jsonify(subjects)
    return jsonify({"error": "Unauthorized"}), 401


# --- NEW: This endpoint finds the timetable_id for the Wi-Fi service ---
@app.route('/api/get-timetable-id/<subject_name>')
def get_timetable_id_for_subject(subject_name):
    if 'loggedin' not in session or session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 401

    teacher_id = session.get('id')
    cursor = mysql.connection.cursor()
    
    # Find the timetable_id from the subject name and teacher
    cursor.execute("""
        SELECT timetable_id FROM timetable 
        WHERE teacher_id = %s AND subject_name = %s
        LIMIT 1 
    """, (teacher_id, subject_name))
    timetable_entry = cursor.fetchone()
    cursor.close()

    if not timetable_entry:
        return jsonify({'error': f'Could not find timetable for {subject_name}'}), 404

    return jsonify({'timetable_id': timetable_entry['timetable_id']})

# --- REMOVED: This old route is no longer needed ---
# @app.route("/update_wifi_attendance", methods=["POST"])
# def update_wifi_attendance():
#     ...
# -------------------- WI-FI ATTENDANCE --------------------
import scapy.all as scapy
from datetime import date

@app.route("/api/scan_wifi/<int:timetable_id>", methods=["GET"])
def scan_wifi(timetable_id):
    if 'loggedin' not in session or session.get('role') != 'teacher':
        return jsonify({"error": "Unauthorized"}), 401

    db = mysql.connection
    cursor = db.cursor()
    
    # Load student MAC mapping
    cursor.execute("SELECT student_id, name, mac_address FROM students")
    students = cursor.fetchall()
    student_map = {s['mac_address'].upper().strip()[:-1]: (s['student_id'], s['name']) for s in students if s['mac_address']}

    # Scan local Wi-Fi network
    arp_request = scapy.ARP(pdst="192.168.148.1/24")  # adjust if your hotspot uses different subnet
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    answered = scapy.srp(broadcast/arp_request, timeout=3, verbose=False)[0]
    connected_macs = [r.hwsrc.upper() for _, r in answered]

    today = date.today()
    present_students, absent_students = [], []

    for mac_key, (sid, name) in student_map.items():
        matched = any(mac.startswith(mac_key) for mac in connected_macs)
        if matched:
            present_students.append(name)
            cursor.execute("""
                UPDATE attendance 
                SET wifi_verified = TRUE 
                WHERE student_id=%s AND timetable_id=%s AND date=%s
            """, (sid, timetable_id, today))
            db.commit()
        else:
            absent_students.append(name)

    return jsonify({
        "status": "ok",
        "present": present_students,
        "absent": absent_students
    })

# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)