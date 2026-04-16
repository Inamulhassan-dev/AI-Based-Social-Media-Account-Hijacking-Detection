import os
import random

import numpy as np
import pandas as pd

# Resolve the backend root regardless of the working directory.
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BACKEND_DIR, "data", "user_behavior_dataset.csv")


def generate_dataset(n_normal=5000, n_suspicious=1000):
    data = []

    for _ in range(n_normal):
        record = generate_normal_record()
        record["is_hijacked"] = 0
        data.append(record)

    for _ in range(n_suspicious):
        record = generate_suspicious_record()
        record["is_hijacked"] = 1
        data.append(record)

    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True)
    os.makedirs(os.path.dirname(_DATA_PATH), exist_ok=True)
    df.to_csv(_DATA_PATH, index=False)
    print(f"Dataset generated: {len(df)} records ({n_normal} normal, {n_suspicious} suspicious)")
    return df


def generate_normal_record():
    login_hour = random.choices(
        range(24),
        weights=[1, 1, 1, 1, 1, 2, 3, 5, 8, 8, 7, 6, 5, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2],
    )[0]

    return {
        "login_hour": login_hour,
        "login_day": random.randint(0, 6),
        "is_new_device": random.choices([0, 1], weights=[95, 5])[0],
        "is_new_location": random.choices([0, 1], weights=[92, 8])[0],
        "is_new_browser": random.choices([0, 1], weights=[90, 10])[0],
        "failed_attempts_before": random.choices([0, 1, 2], weights=[85, 10, 5])[0],
        "login_frequency": round(random.uniform(0.5, 5.0), 2),
        "session_duration": round(random.uniform(5, 120), 2),
        "typing_speed": round(random.uniform(30, 80), 2),
        "mouse_entropy": round(random.uniform(0.3, 0.7), 4),
        "pages_visited": random.randint(2, 30),
        "actions_per_minute": round(random.uniform(1, 10), 2),
        "time_since_last_login": round(random.uniform(0.5, 48), 2),
        "is_vpn": random.choices([0, 1], weights=[90, 10])[0],
        "country_change": 0,
        "device_type_encoded": random.choices([0, 1, 2], weights=[50, 40, 10])[0],
        "hour_sin": np.sin(2 * np.pi * login_hour / 24),
        "hour_cos": np.cos(2 * np.pi * login_hour / 24),
    }


def generate_suspicious_record():
    login_hour = random.choices(
        range(24),
        weights=[5, 8, 8, 8, 8, 5, 3, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 4, 5, 6],
    )[0]

    return {
        "login_hour": login_hour,
        "login_day": random.randint(0, 6),
        "is_new_device": random.choices([0, 1], weights=[20, 80])[0],
        "is_new_location": random.choices([0, 1], weights=[15, 85])[0],
        "is_new_browser": random.choices([0, 1], weights=[25, 75])[0],
        "failed_attempts_before": random.choices([0, 1, 2, 3, 4, 5], weights=[10, 15, 20, 25, 20, 10])[0],
        "login_frequency": round(random.uniform(0.01, 1.0), 2),
        "session_duration": round(random.uniform(0.5, 15), 2),
        "typing_speed": round(random.uniform(10, 150), 2),
        "mouse_entropy": round(random.uniform(0.0, 0.3), 4),
        "pages_visited": random.randint(1, 5),
        "actions_per_minute": round(random.uniform(10, 50), 2),
        "time_since_last_login": round(random.uniform(100, 720), 2),
        "is_vpn": random.choices([0, 1], weights=[40, 60])[0],
        "country_change": random.choices([0, 1], weights=[20, 80])[0],
        "device_type_encoded": random.choices([0, 1, 2], weights=[30, 50, 20])[0],
        "hour_sin": np.sin(2 * np.pi * login_hour / 24),
        "hour_cos": np.cos(2 * np.pi * login_hour / 24),
    }


if __name__ == "__main__":
    generate_dataset()
