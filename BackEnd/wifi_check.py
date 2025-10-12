# pip install scapy pandas openpyxl

import scapy.all as scapy
import pandas as pd

# Load student mapping from Excel or CSV
def load_student_mapping(filename="student.xlsx"):
    df = pd.read_excel(filename)   # or pd.read_csv("student.csv")

    # Create a dictionary, but cut off the last character of MAC for fuzzy matching
    mapping = {}
    for mac, name in zip(df["MAC Address"], df["Student Name"]):
        mac = str(mac).upper().strip()
        if len(mac) >= 2:
            mapping[mac[:-1]] = name   # everything except last hex digit
    return mapping

# Simple ARP scan
def scan(ip_range):
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    answered = scapy.srp(broadcast/arp_request, timeout=2, verbose=False)[0]

    devices = []
    for element in answered:
        devices.append({"IP": element[1].psrc, "MAC": element[1].hwsrc.upper()})
    return devices

def save_with_students(devices, student_map, filename="connected_students.xlsx"):
    df = pd.DataFrame(devices)

    # Fuzzy match: look up by MAC without last digit
    def fuzzy_lookup(mac):
        return student_map.get(mac[:-1], "Unknown")

    df["Student Name"] = df["MAC"].apply(fuzzy_lookup)

    df.to_excel(filename, index=False)
    print(f"[+] Saved results to {filename}")

if __name__ == "__main__":
    target_ip_range = "192.168.1.1/24"   # adjust to your Wi-Fi range
    student_map = load_student_mapping(r"C:\Users\Dhawal\Documents\PBL\Wifi Module\student.xlsx")

    print("[*] Scanning network...")
    devices = scan(target_ip_range)

    if devices:
        save_with_students(devices, student_map, r"C:\Users\Dhawal\Documents\PBL\Wifi Module\connected_students.xlsx")
    else:
        print("[-] No devices found.")
