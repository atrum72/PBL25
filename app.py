from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from BackEnd import wifi_module_db, attendance_db
from datetime import datetime
import hashlib
import os

# -------------------- APP SETUP --------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'supersecretkey'

# -------------------- DATABASE CONFIG --------------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Update with your MySQL username
app.config['MYSQL_PASSWORD'] = 'dhawal@2005'  # Update with your MySQL password
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

# -------------------- WIFI ATTENDANCE --------------------
@app.route('/wifi_scan')
def wifi_scan():
    if 'loggedin' not in session or session.get('role') != 'teacher':
        return redirect(url_for('home'))

    timetable_id = 1  # TODO: dynamic
    wifi_module_db.update_wifi_attendance(mysql.connection, timetable_id)
    return "✅ Wi-Fi attendance scan completed!"

# -------------------- FACE ATTENDANCE --------------------
@app.route('/face_scan', methods=['POST'])
def face_scan():
    if 'loggedin' not in session or session.get('role') != 'teacher':
        return redirect(url_for('home'))

    timetable_id = 1  # TODO: dynamic

    if 'image' not in request.files:
        return "❌ No image uploaded!"

    image = request.files['image']
    path = os.path.join("backend", "temp.jpg")
    image.save(path)

    attendance_db.mark_face_attendance(mysql.connection, timetable_id, image_path=path)
    os.remove(path)
    return "✅ Face attendance updated!"

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

# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)