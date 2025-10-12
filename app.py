from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from BackEnd import wifi_module_db, attendance_db
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- Database config ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_mysql_password",
    database="attendify"
)
cursor = db.cursor(dictionary=True)

# ---------- Login ----------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check teacher
        cursor.execute("SELECT * FROM teachers WHERE email=%s AND password=%s", (email, password))
        teacher = cursor.fetchone()
        if teacher:
            session['user'] = teacher['name']
            session['role'] = 'teacher'
            session['id'] = teacher['teacher_id']
            return redirect(url_for('teacher_dashboard'))

        # Check student
        cursor.execute("SELECT * FROM students WHERE email=%s AND password=%s", (email, password))
        student = cursor.fetchone()
        if student:
            session['user'] = student['name']
            session['role'] = 'student'
            session['id'] = student['student_id']
            return redirect(url_for('student_dashboard'))

        return "Invalid credentials"

    return render_template('login.html')


# ---------- Dashboards ----------
@app.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher_dashboard.html', name=session.get('user'))

@app.route('/student')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student_dashboard.html', name=session.get('user'))


# ---------- Wi-Fi Attendance ----------
@app.route('/wifi_scan')
def wifi_scan():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    # TODO: dynamically get current class timetable_id
    timetable_id = 1
    target_ip_range = "192.168.1.1/24"

    # Run Wi-Fi module
    wifi_module_db.update_wifi_attendance(db, timetable_id)

    return "✅ Wi-Fi attendance scan completed!"


# ---------- Face Recognition Attendance ----------
@app.route('/face_scan', methods=['POST'])
def face_scan():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    timetable_id = 1  # TODO: dynamically get current class timetable_id

    if 'image' not in request.files:
        return "❌ No image uploaded!"

    image = request.files['image']
    path = os.path.join("backend", "temp.jpg")
    image.save(path)

    # Run face recognition module
    attendance_db.mark_face_attendance(db, timetable_id, image_path=path)

    os.remove(path)
    return "✅ Face attendance updated!"


# ---------- View Attendance Reports ----------
@app.route('/attendance_report')
def attendance_report():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

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
    return render_template('attendance_report.html', data=data)


# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)