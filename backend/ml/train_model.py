import json
import os

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

# Resolve paths relative to the backend root regardless of working directory.
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BACKEND_DIR, "data", "user_behavior_dataset.csv")
_MODELS_DIR = os.path.join(_BACKEND_DIR, "ml", "saved_models")

FEATURE_COLUMNS = [
    "login_hour",
    "login_day",
    "is_new_device",
    "is_new_location",
    "is_new_browser",
    "failed_attempts_before",
    "login_frequency",
    "session_duration",
    "typing_speed",
    "mouse_entropy",
    "pages_visited",
    "actions_per_minute",
    "time_since_last_login",
    "is_vpn",
    "country_change",
    "device_type_encoded",
    "hour_sin",
    "hour_cos",
]


def train_all_models():
    os.makedirs(_MODELS_DIR, exist_ok=True)
    df = pd.read_csv(_DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df["is_hijacked"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, os.path.join(_MODELS_DIR, "scaler.pkl"))

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

    results = {}

    rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, class_weight="balanced")
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    print("Random Forest Accuracy:", round(rf_acc, 4))
    print(classification_report(y_test, rf_pred))
    joblib.dump(rf, os.path.join(_MODELS_DIR, "random_forest.pkl"))
    results["random_forest"] = {"accuracy": rf_acc}

    xgb = XGBClassifier(
        n_estimators=100,
        max_depth=10,
        learning_rate=0.1,
        random_state=42,
        scale_pos_weight=len(y[y == 0]) / len(y[y == 1]),
        eval_metric="logloss",
    )
    xgb.fit(X_train, y_train)
    xgb_pred = xgb.predict(X_test)
    xgb_acc = accuracy_score(y_test, xgb_pred)
    print("XGBoost Accuracy:", round(xgb_acc, 4))
    print(classification_report(y_test, xgb_pred))
    joblib.dump(xgb, os.path.join(_MODELS_DIR, "xgboost_model.pkl"))
    results["xgboost"] = {"accuracy": xgb_acc}

    iso = IsolationForest(n_estimators=100, contamination=0.15, random_state=42)
    iso.fit(X_scaled[y == 0])
    joblib.dump(iso, os.path.join(_MODELS_DIR, "isolation_forest.pkl"))
    results["isolation_forest"] = {"contamination": 0.15}

    results["feature_importance"] = dict(zip(FEATURE_COLUMNS, rf.feature_importances_.tolist()))

    with open(os.path.join(_MODELS_DIR, "training_results.json"), "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print("All models trained and saved successfully")
    return results


if __name__ == "__main__":
    train_all_models()
