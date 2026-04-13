import json
from collections import Counter
from datetime import datetime, timedelta

from models.login_activity import LoginActivity
from models.user import User
from database.db import db


class BehaviorAnalyzer:
    @staticmethod
    def update_user_profile(user_id):
        user = User.query.get(user_id)
        if not user:
            return

        cutoff = datetime.utcnow() - timedelta(days=90)
        activities = LoginActivity.query.filter(
            LoginActivity.user_id == user_id,
            LoginActivity.login_success.is_(True),
            LoginActivity.is_suspicious.is_(False),
            LoginActivity.login_time >= cutoff,
        ).all()

        if not activities:
            return

        hours = [a.login_hour for a in activities if a.login_hour is not None]
        hour_counts = Counter(hours)
        threshold = max(len(activities) * 0.1, 1)
        typical_hours = [h for h, count in hour_counts.items() if count >= threshold]
        expanded_hours = set()
        for hour in typical_hours:
            expanded_hours.update([hour, (hour - 1) % 24, (hour + 1) % 24])
        user.typical_login_hours = json.dumps(list(expanded_hours))

        locations = [f"{a.country}-{a.city}" for a in activities if a.country]
        user.typical_locations = json.dumps(list(set(locations)))

        devices = [a.user_agent for a in activities if a.user_agent]
        user.typical_devices = json.dumps(list(set(devices))[:20])

        browsers = [a.browser for a in activities if a.browser]
        user.typical_browsers = json.dumps(list(set(browsers)))

        durations = [a.session_duration for a in activities if a.session_duration]
        if durations:
            user.avg_session_duration = sum(durations) / len(durations)

        if len(activities) >= 2:
            total_days = (activities[-1].login_time - activities[0].login_time).days or 1
            user.avg_activity_frequency = len(activities) / total_days

        db.session.commit()

    @staticmethod
    def get_behavior_summary(user_id):
        user = User.query.get(user_id)
        cutoff_30 = datetime.utcnow() - timedelta(days=30)
        cutoff_7 = datetime.utcnow() - timedelta(days=7)

        total_30 = LoginActivity.query.filter(
            LoginActivity.user_id == user_id,
            LoginActivity.login_time >= cutoff_30,
        ).count()

        suspicious_30 = LoginActivity.query.filter(
            LoginActivity.user_id == user_id,
            LoginActivity.login_time >= cutoff_30,
            LoginActivity.is_suspicious.is_(True),
        ).count()

        recent_activities = LoginActivity.query.filter(
            LoginActivity.user_id == user_id,
            LoginActivity.login_time >= cutoff_7,
        ).order_by(LoginActivity.login_time.desc()).limit(20).all()

        all_activities = LoginActivity.query.filter(
            LoginActivity.user_id == user_id,
            LoginActivity.login_success.is_(True),
        ).all()

        hour_distribution = [0] * 24
        for activity in all_activities:
            if activity.login_hour is not None:
                hour_distribution[activity.login_hour] += 1

        device_counts = Counter([a.device_type for a in all_activities if a.device_type])
        location_counts = Counter([a.country for a in all_activities if a.country])

        risk_trend = [
            {
                "date": a.login_time.isoformat(),
                "risk_score": a.risk_score,
                "is_suspicious": a.is_suspicious,
            }
            for a in recent_activities
        ]

        return {
            "total_logins_30d": total_30,
            "suspicious_logins_30d": suspicious_30,
            "current_risk_score": user.risk_score if user else 0,
            "hour_distribution": hour_distribution,
            "device_distribution": dict(device_counts),
            "location_distribution": dict(location_counts),
            "risk_trend": risk_trend,
            "recent_activities": [a.to_dict() for a in recent_activities],
            "typical_hours": json.loads(user.typical_login_hours) if user and user.typical_login_hours else [],
            "typical_locations": json.loads(user.typical_locations) if user and user.typical_locations else [],
        }
