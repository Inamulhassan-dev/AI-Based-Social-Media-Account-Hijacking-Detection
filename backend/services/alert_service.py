import json
import logging
from datetime import datetime

from database.db import db
from models.alert import Alert

logger = logging.getLogger(__name__)


class AlertService:
    @staticmethod
    def create_alert(user_id, activity_id, risk_data):
        risk_score = risk_data["risk_score"]
        risk_level = risk_data["risk_level"]
        risk_factors = risk_data["risk_factors"]

        alert_types = [factor["factor"] for factor in risk_factors]
        if "Impossible Travel Detected" in alert_types:
            alert_type = "impossible_travel"
        elif "New Location Detected" in alert_types:
            alert_type = "unusual_location"
        elif "New Device Detected" in alert_types:
            alert_type = "new_device"
        elif "Multiple Failed Attempts" in alert_types:
            alert_type = "brute_force"
        else:
            alert_type = "suspicious_login"

        title = AlertService._generate_title(alert_type)
        message = AlertService._generate_message(risk_factors)

        alert = Alert(
            user_id=user_id,
            activity_id=activity_id,
            alert_type=alert_type,
            severity=risk_level,
            title=title,
            message=message,
            details=json.dumps(risk_factors),
            risk_score=risk_score,
        )

        db.session.add(alert)
        db.session.commit()
        logger.info("Alert created for user %s: %s", user_id, title)
        return alert

    @staticmethod
    def _generate_title(alert_type):
        titles = {
            "impossible_travel": "Impossible Travel Detected",
            "unusual_location": "Login from Unusual Location",
            "new_device": "Login from New Device",
            "brute_force": "Multiple Failed Login Attempts",
            "suspicious_login": "Suspicious Login Activity",
            "hijacking": "Potential Account Hijacking",
        }
        return titles.get(alert_type, "Security Alert")

    @staticmethod
    def _generate_message(risk_factors):
        return "\n".join([f"- {rf['factor']}: {rf['detail']}" for rf in risk_factors])

    @staticmethod
    def get_user_alerts(user_id, limit=50, unread_only=False):
        query = Alert.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
        return [a.to_dict() for a in alerts]

    @staticmethod
    def mark_as_read(alert_id, user_id):
        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            alert.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def resolve_alert(alert_id, resolved_by, action_taken):
        alert = Alert.query.get(alert_id)
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = resolved_by
            alert.action_taken = action_taken
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_alert_stats(user_id=None):
        query = Alert.query
        if user_id:
            query = query.filter_by(user_id=user_id)

        total = query.count()
        unread = query.filter_by(is_read=False).count()
        critical = query.filter_by(severity="critical").count()
        high = query.filter_by(severity="high").count()
        resolved = query.filter_by(is_resolved=True).count()

        return {
            "total": total,
            "unread": unread,
            "critical": critical,
            "high": high,
            "resolved": resolved,
            "unresolved": total - resolved,
        }
