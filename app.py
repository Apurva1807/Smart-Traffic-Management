from flask import Flask, render_template, redirect, request, jsonify
import csv
import os
import smtplib
import time
import random
from email.message import EmailMessage

app = Flask(__name__)

# =========================
# PATH CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
JUNCTIONS_FILE = os.path.join(DATA_DIR, "traffic_data.csv")

# =========================
# EMAIL CONFIG
# =========================
EMAIL_ENABLED = False                 # 🔴 controlled from UI
EMAIL_COOLDOWN = 600                  # 10 minutes

SENDER_EMAIL = "apurvasamudalapalem999@gmail.com"
SENDER_APP_PASSWORD = "password"     # Gmail App Password

RECEIVER_EMAILS = [
    "achyutha0506@gmail.com",
    "sujitha4298@gmail.com"
]

LAST_EMAIL_TIME = 0

# =========================
# FAKE ALERT POOL
# =========================
FAKE_ALERTS = [
    "Heavy congestion detected at East Lane",
    "Emergency vehicle approaching South Lane",
    "Traffic slowdown near Central Junction",
    "Accident cleared at West Lane",
    "Alternate route recommended due to congestion"
]

# =========================
# CSV READER
# =========================
def read_csv(file_path):
    data = []
    if not os.path.exists(file_path):
        return data

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

# =========================
# EMAIL SENDER
# =========================
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
Smart Traffic Management Alert

{message}

Time: {time.strftime('%H:%M:%S')}

Please plan your route accordingly.
"""
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)

        LAST_EMAIL_TIME = now
        print("✅ Alert email sent")

    except Exception as e:
        print("❌ Email error:", e)

# =========================
# API: TOGGLE EMAIL ALERTS
# =========================
@app.route("/toggle-email-alerts", methods=["POST"])
def toggle_email_alerts():
    global EMAIL_ENABLED
    data = request.get_json()
    EMAIL_ENABLED = bool(data.get("enabled"))
    print("📧 Email Alerts Enabled:", EMAIL_ENABLED)
    return jsonify({"status": "success", "enabled": EMAIL_ENABLED})

# =========================
# HOME
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

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
    return render_template(
        "user/user_dashboard.html",
        email_enabled=EMAIL_ENABLED
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

    # 🔥 SIMULATED ALERT
    alert_message = random.choice(FAKE_ALERTS)
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

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)