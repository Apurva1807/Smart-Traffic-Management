import pandas as pd
import random
import time
from datetime import datetime

TRAFFIC_FILE = "data/traffic_data.csv"
ALERT_FILE = "data/alerts_log.csv"

def simulate_traffic():
    while True:
        df = pd.read_csv(TRAFFIC_FILE)

        for index, row in df.iterrows():
            vehicle_count = random.randint(5, 50)

            if vehicle_count > 30:
                congestion = "High"
                log_alert("CONGESTION",
                          f"High congestion at {row['junction']} lane {row['lane']}")
            elif vehicle_count > 15:
                congestion = "Medium"
            else:
                congestion = "Low"

            df.at[index, "vehicle_count"] = vehicle_count
            df.at[index, "congestion_level"] = congestion
            df.at[index, "timestamp"] = datetime.now().strftime("%H:%M:%S")

        # Random ambulance alert
        if random.choice([True, False]):
            log_alert("AMBULANCE",
                      "🚑 Ambulance detected, please clear the lane")

        df.to_csv(TRAFFIC_FILE, index=False)
        time.sleep(10)  # update every 10 seconds


def log_alert(alert_type, message):
    alert_df = pd.DataFrame([{
        "type": alert_type,
        "message": message,
        "time": datetime.now().strftime("%H:%M:%S")
    }])

    try:
        existing = pd.read_csv(ALERT_FILE)
        updated = pd.concat([existing, alert_df], ignore_index=True)
    except:
        updated = alert_df

    updated.to_csv(ALERT_FILE, index=False)