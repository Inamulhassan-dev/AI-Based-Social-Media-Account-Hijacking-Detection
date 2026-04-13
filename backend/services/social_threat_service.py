import json
from datetime import datetime, timedelta

from models.login_activity import LoginActivity


class SocialThreatService:
    """Build social-media-focused risk insights from login telemetry."""

    @staticmethod
    def get_social_insights(user_id):
        cutoff = datetime.utcnow() - timedelta(days=30)
        activities = (
            LoginActivity.query.filter(
                LoginActivity.user_id == user_id,
                LoginActivity.login_time >= cutoff,
            )
            .order_by(LoginActivity.login_time.desc())
            .all()
        )

        if not activities:
            return {
                "window_days": 30,
                "total_sessions": 0,
                "takeover_risk_score": 0,
                "risk_level": "low",
                "signals": {
                    "suspicious_login_rate": 0,
                    "new_device_rate": 0,
                    "new_location_rate": 0,
                    "vpn_usage_rate": 0,
                    "off_hours_activity_rate": 0,
                    "impossible_travel_count": 0,
                },
                "platform_risk_tags": ["no_recent_activity"],
                "recommended_actions": [
                    "Keep 2FA enabled for all social accounts",
                    "Review connected devices and revoke old sessions",
                    "Enable login alerts for unusual activity",
                ],
                "recent_high_risk_sessions": [],
            }

        total = len(activities)
        suspicious = sum(1 for a in activities if a.is_suspicious)
        new_device = sum(1 for a in activities if a.is_new_device)
        new_location = sum(1 for a in activities if a.is_new_location)
        vpn_usage = sum(1 for a in activities if a.is_vpn)
        off_hours = sum(1 for a in activities if (a.login_hour is not None and (a.login_hour <= 5 or a.login_hour >= 23)))

        impossible_travel_count = 0
        for activity in activities:
            try:
                factors = json.loads(activity.risk_factors or "[]")
            except json.JSONDecodeError:
                factors = []
            if any(f.get("factor") == "Impossible Travel Detected" for f in factors if isinstance(f, dict)):
                impossible_travel_count += 1

        suspicious_rate = suspicious / total
        new_device_rate = new_device / total
        new_location_rate = new_location / total
        vpn_rate = vpn_usage / total
        off_hours_rate = off_hours / total

        takeover_risk_score = (
            suspicious_rate * 0.35
            + new_device_rate * 0.15
            + new_location_rate * 0.2
            + vpn_rate * 0.15
            + off_hours_rate * 0.1
            + min(impossible_travel_count / max(1, total), 1) * 0.05
        )

        risk_level = "low"
        if takeover_risk_score >= 0.75:
            risk_level = "critical"
        elif takeover_risk_score >= 0.5:
            risk_level = "high"
        elif takeover_risk_score >= 0.3:
            risk_level = "medium"

        platform_risk_tags = []
        if new_device_rate >= 0.3:
            platform_risk_tags.append("new_device_spike")
        if new_location_rate >= 0.25:
            platform_risk_tags.append("geo_anomaly")
        if impossible_travel_count > 0:
            platform_risk_tags.append("impossible_travel")
        if off_hours_rate >= 0.4:
            platform_risk_tags.append("late_night_activity")
        if vpn_rate >= 0.35:
            platform_risk_tags.append("proxy_vpn_heavy")
        if suspicious_rate >= 0.4:
            platform_risk_tags.append("possible_takeover_pattern")
        if not platform_risk_tags:
            platform_risk_tags.append("baseline_normal")

        recommended_actions = [
            "Enable app-based 2FA on all social media accounts",
            "Review unknown devices and force logout inactive sessions",
            "Change password if you see unfamiliar location/device alerts",
        ]

        if risk_level in {"high", "critical"}:
            recommended_actions.insert(0, "Immediately revoke active sessions and rotate credentials")

        recent_high_risk_sessions = []
        for activity in activities[:10]:
            if activity.risk_score >= 0.5:
                recent_high_risk_sessions.append(
                    {
                        "login_time": activity.login_time.isoformat() if activity.login_time else None,
                        "country": activity.country,
                        "city": activity.city,
                        "risk_score": round(activity.risk_score, 4),
                        "is_new_device": bool(activity.is_new_device),
                        "is_new_location": bool(activity.is_new_location),
                        "is_vpn": bool(activity.is_vpn),
                    }
                )

        return {
            "window_days": 30,
            "total_sessions": total,
            "takeover_risk_score": round(min(takeover_risk_score, 1.0), 4),
            "risk_level": risk_level,
            "signals": {
                "suspicious_login_rate": round(suspicious_rate, 4),
                "new_device_rate": round(new_device_rate, 4),
                "new_location_rate": round(new_location_rate, 4),
                "vpn_usage_rate": round(vpn_rate, 4),
                "off_hours_activity_rate": round(off_hours_rate, 4),
                "impossible_travel_count": impossible_travel_count,
            },
            "platform_risk_tags": platform_risk_tags,
            "recommended_actions": recommended_actions,
            "recent_high_risk_sessions": recent_high_risk_sessions,
        }
