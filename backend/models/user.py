import json
from datetime import datetime

from database.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default="user")
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    lock_reason = db.Column(db.String(255), nullable=True)
    locked_at = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)

    typical_login_hours = db.Column(db.Text, default="[]")
    typical_ips = db.Column(db.Text, default="[]")
    typical_devices = db.Column(db.Text, default="[]")
    typical_locations = db.Column(db.Text, default="[]")
    typical_browsers = db.Column(db.Text, default="[]")
    avg_session_duration = db.Column(db.Float, default=0.0)
    avg_activity_frequency = db.Column(db.Float, default=0.0)

    risk_score = db.Column(db.Float, default=0.0)
    total_logins = db.Column(db.Integer, default=0)
    suspicious_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    login_activities = db.relationship("LoginActivity", backref="user", lazy="dynamic")
    alerts = db.relationship("Alert", backref="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "is_locked": self.is_locked,
            "lock_reason": self.lock_reason,
            "two_factor_enabled": self.two_factor_enabled,
            "risk_score": self.risk_score,
            "total_logins": self.total_logins,
            "suspicious_count": self.suspicious_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "typical_login_hours": json.loads(self.typical_login_hours) if self.typical_login_hours else [],
            "typical_locations": json.loads(self.typical_locations) if self.typical_locations else [],
        }
