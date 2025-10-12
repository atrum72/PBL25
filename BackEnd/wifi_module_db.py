# pip install scapy pandas mysql-connector-python
import scapy.all as scapy
import mysql.connector
from datetime import date

def load_student_mac(db):
    """
    Returns a dictionary mapping last-1-char stripped MAC -> student_id
    """
    cursor = db.cursor()
    cursor.execute("SELECT student_id, mac_address FROM students")
    mapping = {}
    for student_id, mac in cursor.fetchall():
        if mac:
            mapping[mac.upper().strip()[:-1]] = student_id
    return mapping

def scan_network(ip_range="192.168.1.1/24"):
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    answered = scapy.srp(broadcast/arp_request, timeout=2, verbose=False)[0]
    
    devices = []
    for _, rcv in answered:
        devices.append(rcv.hwsrc.upper())
    return devices

def update_wifi_attendance(db, timetable_id):
    student_map = load_student_mac(db)
    connected_macs = scan_network()
    today = date.today()
    
    cursor = db.cursor()
    for mac in connected_macs:
        mac_key = mac[:-1]  # last char stripped
        student_id = student_map.get(mac_key)
        if student_id:
            cursor.execute("""
                UPDATE attendance
                SET wifi_verified = TRUE
                WHERE student_id=%s AND timetable_id=%s AND date=%s
            """, (student_id, timetable_id, today))
    db.commit()
    print("[+] Wi-Fi attendance updated")