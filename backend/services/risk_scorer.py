import json
from datetime import datetime

from models.login_activity import LoginActivity


class RiskScorer:
    WEIGHTS = {
        "new_device": 0.20,
        "new_location": 0.25,
        "unusual_time": 0.15,
        "failed_attempts": 0.15,
        "vpn_usage": 0.10,
        "rapid_geo_change": 0.10,
        "abnormal_behavior": 0.05,
    }

    @staticmethod
    def calculate_risk(user, login_data):
        risk_factors = []
        total_risk = 0.0

        typical_devices = json.loads(user.typical_devices) if user.typical_devices else []
        device_fingerprint = login_data.get("device_fingerprint", "")
        if device_fingerprint and device_fingerprint not in typical_devices:
            total_risk += RiskScorer.WEIGHTS["new_device"]
            risk_factors.append({
                "factor": "New Device Detected",
                "severity": "medium",
                "score": RiskScorer.WEIGHTS["new_device"],
                "detail": "Login from unrecognized device",
            })

        typical_locations = json.loads(user.typical_locations) if user.typical_locations else []
        current_location = f"{login_data.get('country', '')}-{login_data.get('city', '')}"
        if current_location and current_location not in typical_locations and typical_locations:
            total_risk += RiskScorer.WEIGHTS["new_location"]
            risk_factors.append({
                "factor": "New Location Detected",
                "severity": "high",
                "score": RiskScorer.WEIGHTS["new_location"],
                "detail": f"Login from {login_data.get('city', 'unknown')}, {login_data.get('country', 'unknown')}",
            })

        typical_hours = json.loads(user.typical_login_hours) if user.typical_login_hours else []
        current_hour = datetime.utcnow().hour
        if typical_hours and current_hour not in typical_hours:
            total_risk += RiskScorer.WEIGHTS["unusual_time"]
            risk_factors.append({
                "factor": "Unusual Login Time",
                "severity": "medium",
                "score": RiskScorer.WEIGHTS["unusual_time"],
                "detail": f"Login at {current_hour}:00 UTC (unusual for this user)",
            })

        if user.failed_login_attempts >= 3:
            factor_score = min(RiskScorer.WEIGHTS["failed_attempts"] * (user.failed_login_attempts / 3), 0.3)
            total_risk += factor_score
            risk_factors.append({
                "factor": "Multiple Failed Attempts",
                "severity": "high",
                "score": factor_score,
                "detail": f"{user.failed_login_attempts} failed login attempts",
            })

        if login_data.get("is_vpn", False):
            total_risk += RiskScorer.WEIGHTS["vpn_usage"]
            risk_factors.append({
                "factor": "VPN/Proxy Detected",
                "severity": "low",
                "score": RiskScorer.WEIGHTS["vpn_usage"],
                "detail": "Login through VPN or proxy server",
            })

        last_login = LoginActivity.query.filter_by(user_id=user.id, login_success=True).order_by(LoginActivity.login_time.desc()).first()
        if last_login and last_login.country and login_data.get("country"):
            time_diff = (datetime.utcnow() - last_login.login_time).total_seconds() / 3600
            if last_login.country != login_data.get("country") and time_diff < 2:
                total_risk += RiskScorer.WEIGHTS["rapid_geo_change"]
                risk_factors.append({
                    "factor": "Impossible Travel Detected",
                    "severity": "critical",
                    "score": RiskScorer.WEIGHTS["rapid_geo_change"],
                    "detail": f"Country changed from {last_login.country} to {login_data.get('country')} in {time_diff:.1f} hours",
                })

        total_risk = min(total_risk, 1.0)

        return {
            "risk_score": round(total_risk, 4),
            "risk_level": RiskScorer._get_risk_level(total_risk),
            "risk_factors": risk_factors,
            "is_suspicious": total_risk >= 0.5,
            "should_lock": total_risk >= 0.8,
            "requires_2fa": total_risk >= 0.5,
        }

    @staticmethod
    def _get_risk_level(score):
        if score >= 0.8:
            return "critical"
        if score >= 0.5:
            return "high"
        if score >= 0.3:
            return "medium"
        return "low"
