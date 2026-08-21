from flask import Flask, render_template, redirect, request
import csv
import os
import smtplib
import time
import webbrowser
import threading
from email.message import EmailMessage
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

# =========================
# EMAIL CONFIG
# =========================
EMAIL_ENABLED = True        # TRUE = send email, FALSE = stop email
EMAIL_COOLDOWN = 60        # 10 minutes cooldown

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD")

RECEIVER_EMAILS = [
    "sujitha4298@gmail.com",
    "achyutha0506@gmail.com"
]

LAST_EMAIL_TIME = 0

# =========================
# PATH CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
JUNCTIONS_FILE = os.path.join(DATA_DIR, "traffic_data.csv")

# =========================
# CSV READER
# =========================
def read_csv(file_path):
    data = []
    if not os.path.exists(file_path):
        return data

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

# =========================
# HOME PAGE
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# LOGIN PAGE
# =========================
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

# =========================
# LOGIN HANDLER
# =========================
@app.route("/login", methods=["POST"])
def login_handler():
    role = request.form.get("role")

    if role == "admin":
        return redirect("/admin-dashboard")
    elif role == "user":
        return redirect("/user-dashboard")

    return redirect("/login")

# =========================
# USER DASHBOARD
# =========================
@app.route("/user-dashboard")
def user_dashboard():
    data = read_csv(JUNCTIONS_FILE)

    junctions = []
    for d in data:
        junctions.append({
            "name": d.get("junction", ""),
            "vehicles": int(d.get("vehicles", 0)),
            "wait": int(d.get("wait_time", 0))
        })

    return render_template(
        "user/user_dashboard.html",
        junctions=junctions
    )

# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin-dashboard")
def admin_dashboard():
    data = read_csv(JUNCTIONS_FILE)

    junction_names = []
    traffic_values = []
    wait_times = []

    for d in data:
        junction_names.append(d.get("junction", ""))
        traffic_values.append(int(d.get("vehicles", 0)))
        wait_times.append(int(d.get("wait_time", 0)))

    alert_message = "Heavy traffic detected at West Lane"
    send_email_alert(alert_message)

    alerts = [
        {"type": "Traffic", "message": alert_message, "time": "Just now"}
    ]

    avg_wait = sum(wait_times) // len(wait_times) if wait_times else 0

    return render_template(
        "admin/admin_dashboard.html",
        total_junctions=len(junction_names),
        avg_wait_time=avg_wait,
        system_efficiency=85,
        junction_names=junction_names,
        traffic_values=traffic_values,
        wait_times=wait_times,
        alerts=alerts
    )

def send_email_alert(message):
    global LAST_EMAIL_TIME

    if not EMAIL_ENABLED:
        return

    now = time.time()
    if now - LAST_EMAIL_TIME < EMAIL_COOLDOWN:
        return

    try:
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(RECEIVER_EMAILS)
        msg["Subject"] = "🚦 Smart Traffic Alert"
        msg.set_content(
            f"""
Smart Traffic Alert

{message}

Time: {time.strftime('%H:%M:%S')}
"""
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)

        LAST_EMAIL_TIME = now
        print("✅ Email alert sent")

    except Exception as e:
        print("❌ Email error:", e)

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    threading.Timer(
        1.0,
        lambda: webbrowser.open("http://127.0.0.1:5000")
    ).start()

    app.run(debug=True, use_reloader=False)