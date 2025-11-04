# wifi_backend.py
from flask import Flask, jsonify, request
import scapy.all as scapy
import mysql.connector
from datetime import date

app = Flask(__name__)

def load_student_mac(db):
    cursor = db.cursor()
    cursor.execute("SELECT student_id, name, mac_address FROM students")
    data = cursor.fetchall()
    mapping = {mac.upper().strip()[:-1]: (student_id, name) for student_id, name, mac in data if mac}
    return mapping

def scan_network(ip_range="192.168.1.1/24"):
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    answered = scapy.srp(broadcast/arp_request, timeout=5, verbose=False)[0]
    return [rcv.hwsrc.upper() for _, rcv in answered]

@app.route("/start_lecture", methods=["POST"])
def start_lecture():
    timetable_id = request.json.get("timetable_id", 1)
    ip_range = request.json.get("ip_range", "192.168.1.1/24")

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sanju",
        database="attendify"
    )

    student_map = load_student_mac(db)
    connected_macs = scan_network(ip_range)
    today = date.today()

    present, absent = [], []

    for mac_key, (student_id, name) in student_map.items():
        if any(mac.startswith(mac_key) for mac in connected_macs):
            present.append(name)
            cursor = db.cursor()
            cursor.execute("""
                UPDATE attendance
                SET wifi_verified = TRUE
                WHERE student_id=%s AND timetable_id=%s AND date=%s
            """, (student_id, timetable_id, today))
        else:
            absent.append(name)

    db.commit()
    db.close()

    return jsonify({
        "present": present,
        "absent": absent,
        "count_present": len(present),
        "count_absent": len(absent)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
