import mysql.connector
from datetime import datetime
import schedule
import time

# ---------- STEP 1: Connect to MySQL ----------
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",           # <-- Change only if needed
            password="",           # <-- Put your MySQL password here (if any)
            database="attendify"
        )
        print("[✅] Connected to MySQL successfully.")
        return conn
    except mysql.connector.Error as err:
        print(f"[❌] Database connection failed: {err}")
        return None

# ---------- STEP 2: Auto Attendance Insertion ----------
def auto_insert_attendance():
    conn = get_connection()
    if not conn:
        print("[⚠️] Skipping auto attendance due to DB connection error.\n")
        return

    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    day = datetime.now().strftime("%A")

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto inserting attendance for {day}, {today}...")

    # Get today's timetable entries
    cursor.execute("SELECT timetable_id FROM timetable WHERE day_of_week = %s", (day,))
    timetable_ids = [row[0] for row in cursor.fetchall()]

    if not timetable_ids:
        print(f"[ℹ️] No classes scheduled today ({day}).")
        conn.close()
        return

    # Insert attendance for each student in each class
    cursor.execute("SELECT student_id FROM students")
    students = cursor.fetchall()
    total_inserted = 0

    for t_id in timetable_ids:
        for (s_id,) in students:
            cursor.execute("""
                INSERT IGNORE INTO attendance (student_id, timetable_id, date)
                VALUES (%s, %s, %s)
            """, (s_id, t_id, today))
            total_inserted += cursor.rowcount

    conn.commit()
    conn.close()

    print(f"[✅] Attendance records auto-inserted successfully ({total_inserted} rows).\n")

# ---------- STEP 3: Scheduler ----------
def main():
    print("===================================================")
    print("🕒 Auto Attendance Scheduler Started")
    print("===================================================")
    print("This script will automatically insert attendance records daily.")
    print("You can keep it running in background or run manually anytime.\n")

    # Run immediately once (for testing)
    auto_insert_attendance()

    # Schedule daily at 07:00 AM
    schedule.every().day.at("07:00").do(auto_insert_attendance)

    print("[⏳] Waiting for scheduled time (07:00 AM daily)...\n")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
