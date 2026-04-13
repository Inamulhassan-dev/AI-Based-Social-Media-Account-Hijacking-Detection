from datetime import datetime

from database.db import db


class LoginActivity(db.Model):
    __tablename__ = "login_activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    ip_address = db.Column(db.String(45), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    login_hour = db.Column(db.Integer)
    login_day = db.Column(db.Integer)

    device_type = db.Column(db.String(50))
    browser = db.Column(db.String(100))
    operating_system = db.Column(db.String(100))
    user_agent = db.Column(db.Text)
    screen_resolution = db.Column(db.String(20))

    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timezone = db.Column(db.String(50))

    typing_speed = db.Column(db.Float, default=0.0)
    mouse_movement_pattern = db.Column(db.Float, default=0.0)
    session_duration = db.Column(db.Float, default=0.0)
    pages_visited = db.Column(db.Integer, default=0)
    actions_count = db.Column(db.Integer, default=0)

    is_suspicious = db.Column(db.Boolean, default=False)
    risk_score = db.Column(db.Float, default=0.0)
    anomaly_score = db.Column(db.Float, default=0.0)
    risk_factors = db.Column(db.Text, default="[]")

    login_success = db.Column(db.Boolean, default=True)
    is_new_device = db.Column(db.Boolean, default=False)
    is_new_location = db.Column(db.Boolean, default=False)
    is_unusual_time = db.Column(db.Boolean, default=False)
    is_vpn = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "login_time": self.login_time.isoformat() if self.login_time else None,
            "login_hour": self.login_hour,
            "login_day": self.login_day,
            "device_type": self.device_type,
            "browser": self.browser,
            "operating_system": self.operating_system,
            "country": self.country,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "typing_speed": self.typing_speed,
            "session_duration": self.session_duration,
            "is_suspicious": self.is_suspicious,
            "risk_score": self.risk_score,
            "anomaly_score": self.anomaly_score,
            "risk_factors": self.risk_factors,
            "is_new_device": self.is_new_device,
            "is_new_location": self.is_new_location,
            "is_unusual_time": self.is_unusual_time,
            "login_success": self.login_success,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
