from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/teacher')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

@app.route('/student')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/attendance')
def attendance_report():
    return render_template('attendance_report.html')

if __name__ == '__main__':
    app.run(debug=True)