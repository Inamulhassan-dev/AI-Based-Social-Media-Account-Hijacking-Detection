import logging
import os

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class HijackingPredictor:
    def __init__(self):
        self.models_loaded = False
        self.scaler = None
        self.rf_model = None
        self.xgb_model = None
        self.iso_model = None
        self._load_models()

    def _load_models(self):
        try:
            model_dir = os.path.join(os.path.dirname(__file__), "saved_models")
            scaler_path = os.path.join(model_dir, "scaler.pkl")
            rf_path = os.path.join(model_dir, "random_forest.pkl")
            xgb_path = os.path.join(model_dir, "xgboost_model.pkl")
            iso_path = os.path.join(model_dir, "isolation_forest.pkl")

            paths = [scaler_path, rf_path, xgb_path, iso_path]
            if all(os.path.exists(path) for path in paths):
                self.scaler = joblib.load(scaler_path)
                self.rf_model = joblib.load(rf_path)
                self.xgb_model = joblib.load(xgb_path)
                self.iso_model = joblib.load(iso_path)
                self.models_loaded = True
                logger.info("ML models loaded")
            else:
                logger.warning("ML models not found. Train first.")
        except Exception as exc:
            logger.error("Error loading models: %s", exc)

    def predict(self, features_dict):
        if not self.models_loaded:
            return self._default_prediction()

        try:
            feature_order = [
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

            hour = features_dict.get("login_hour", 12)
            features_dict["hour_sin"] = np.sin(2 * np.pi * hour / 24)
            features_dict["hour_cos"] = np.cos(2 * np.pi * hour / 24)

            features = np.array([[features_dict.get(column, 0) for column in feature_order]])
            features_scaled = self.scaler.transform(features)

            rf_prob = self.rf_model.predict_proba(features_scaled)[0][1]
            xgb_prob = self.xgb_model.predict_proba(features_scaled)[0][1]
            iso_score = self.iso_model.decision_function(features_scaled)[0]
            iso_anomaly = 1 if iso_score < 0 else 0
            iso_normalized = max(0, min(1, -iso_score))

            ensemble_score = (rf_prob * 0.4) + (xgb_prob * 0.4) + (iso_normalized * 0.2)
            is_hijacked = ensemble_score >= 0.5

            return {
                "is_hijacked": bool(is_hijacked),
                "ensemble_score": round(float(ensemble_score), 4),
                "random_forest_prob": round(float(rf_prob), 4),
                "xgboost_prob": round(float(xgb_prob), 4),
                "isolation_forest_score": round(float(iso_normalized), 4),
                "confidence": round(float(max(ensemble_score, 1 - ensemble_score)), 4),
                "model_agreement": sum([rf_prob > 0.5, xgb_prob > 0.5, iso_anomaly]) / 3,
            }
        except Exception as exc:
            logger.error("Prediction error: %s", exc)
            return self._default_prediction()

    def _default_prediction(self):
        return {
            "is_hijacked": False,
            "ensemble_score": 0.0,
            "random_forest_prob": 0.0,
            "xgboost_prob": 0.0,
            "isolation_forest_score": 0.0,
            "confidence": 0.5,
            "model_agreement": 0.0,
        }


predictor = HijackingPredictor()
