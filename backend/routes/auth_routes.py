import json
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from database.db import db
from ml.predict import predictor
from models.login_activity import LoginActivity
from models.user import User
from services.alert_service import AlertService
from services.behavior_analyzer import BehaviorAnalyzer
from services.geolocation_service import get_geolocation
from services.risk_scorer import RiskScorer
from utils.helpers import generate_device_fingerprint, parse_user_agent, validate_email, validate_password
from utils.jwt_handler import generate_tokens

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    valid, message = validate_password(password)
    if not valid:
        return jsonify({"error": message}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role="admin" if User.query.count() == 0 else "user",
    )
    db.session.add(user)
    db.session.commit()

    access_token, refresh_token = generate_tokens(user.id, user.role)

    return (
        jsonify(
            {
                "message": "Registration successful",
                "user": user.to_dict(),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ),
        201,
    )


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")

    client_data = {
        "user_agent": request.headers.get("User-Agent", ""),
        "ip_address": request.remote_addr or "127.0.0.1",
        "screen_resolution": data.get("screen_resolution", "unknown"),
        "timezone": data.get("timezone", "UTC"),
        "typing_speed": data.get("typing_speed", 0),
        "mouse_entropy": data.get("mouse_entropy", 0),
    }

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if user.is_locked:
        return jsonify({"error": "Account is locked due to suspicious activity", "lock_reason": user.lock_reason}), 403

    if not bcrypt.check_password_hash(user.password_hash, password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.is_locked = True
            user.lock_reason = "Too many failed login attempts"
            user.locked_at = datetime.utcnow()
        db.session.commit()
        _log_activity(user.id, client_data, success=False)
        return jsonify({"error": "Invalid credentials", "attempts_remaining": max(0, 5 - user.failed_login_attempts)}), 401

    geo_data = get_geolocation(client_data["ip_address"])
    device_info = parse_user_agent(client_data["user_agent"])

    login_data = {
        **client_data,
        **geo_data,
        **device_info,
        "device_fingerprint": generate_device_fingerprint(client_data),
    }

    risk_result = RiskScorer.calculate_risk(user, login_data)

    ml_features = {
        "login_hour": datetime.utcnow().hour,
        "login_day": datetime.utcnow().weekday(),
        "is_new_device": 1 if any(r["factor"] == "New Device Detected" for r in risk_result.get("risk_factors", [])) else 0,
        "is_new_location": 1 if any(r["factor"] == "New Location Detected" for r in risk_result.get("risk_factors", [])) else 0,
        "is_new_browser": 0,
        "failed_attempts_before": user.failed_login_attempts,
        "login_frequency": user.avg_activity_frequency or 1.0,
        "session_duration": user.avg_session_duration or 30.0,
        "typing_speed": client_data.get("typing_speed", 50),
        "mouse_entropy": client_data.get("mouse_entropy", 0.5),
        "pages_visited": 1,
        "actions_per_minute": 5.0,
        "time_since_last_login": _hours_since_last_login(user),
        "is_vpn": 1 if geo_data.get("is_vpn") else 0,
        "country_change": 1 if any(r["factor"] == "Impossible Travel Detected" for r in risk_result.get("risk_factors", [])) else 0,
        "device_type_encoded": {"desktop": 0, "mobile": 1, "tablet": 2}.get(device_info.get("device_type", "desktop"), 0),
    }

    ml_prediction = predictor.predict(ml_features)
    combined_risk = (risk_result["risk_score"] * 0.5) + (ml_prediction["ensemble_score"] * 0.5)

    activity = _log_activity(
        user.id,
        login_data,
        success=True,
        risk_score=combined_risk,
        anomaly_score=ml_prediction["ensemble_score"],
        risk_factors=risk_result["risk_factors"],
    )

    alert = None
    if combined_risk >= 0.5:
        risk_result["risk_score"] = combined_risk
        alert = AlertService.create_alert(user.id, activity.id, risk_result)

    if combined_risk >= 0.8:
        user.is_locked = True
        user.lock_reason = "AI detected potential account hijacking"
        user.locked_at = datetime.utcnow()
        db.session.commit()
        return (
            jsonify(
                {
                    "error": "Account locked due to suspicious activity. Please verify your identity.",
                    "risk_score": combined_risk,
                    "alert": alert.to_dict() if alert else None,
                    "requires_verification": True,
                }
            ),
            403,
        )

    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    user.total_logins += 1
    user.risk_score = combined_risk
    db.session.commit()

    BehaviorAnalyzer.update_user_profile(user.id)

    access_token, refresh_token = generate_tokens(user.id, user.role)

    response_data = {
        "message": "Login successful",
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "risk_assessment": {
            "risk_score": round(combined_risk, 4),
            "risk_level": risk_result["risk_level"],
            "risk_factors": risk_result["risk_factors"],
            "ml_prediction": ml_prediction,
        },
    }

    if combined_risk >= 0.3:
        response_data["security_warning"] = {
            "message": "Some unusual activity detected. Please verify if this was you.",
            "alert": alert.to_dict() if alert else None,
        }

    return jsonify(response_data), 200


@auth_bp.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/api/auth/unlock", methods=["POST"])
@jwt_required()
def unlock_account():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json() or {}
    user_id = data.get("user_id")
    user = User.query.get(user_id)
    if user:
        user.is_locked = False
        user.lock_reason = None
        user.locked_at = None
        user.failed_login_attempts = 0
        db.session.commit()
        return jsonify({"message": f"Account {user.username} unlocked"}), 200
    return jsonify({"error": "User not found"}), 404


@auth_bp.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


def _log_activity(user_id, login_data, success=True, risk_score=0, anomaly_score=0, risk_factors=None):
    now = datetime.utcnow()
    factors = risk_factors or []

    activity = LoginActivity(
        user_id=user_id,
        ip_address=login_data.get("ip_address", "0.0.0.0"),
        login_time=now,
        login_hour=now.hour,
        login_day=now.weekday(),
        device_type=login_data.get("device_type", "unknown"),
        browser=login_data.get("browser", "unknown"),
        operating_system=login_data.get("operating_system", "unknown"),
        user_agent=login_data.get("user_agent", ""),
        screen_resolution=login_data.get("screen_resolution", ""),
        country=login_data.get("country", "Unknown"),
        city=login_data.get("city", "Unknown"),
        latitude=login_data.get("latitude", 0),
        longitude=login_data.get("longitude", 0),
        timezone=login_data.get("timezone", "UTC"),
        typing_speed=login_data.get("typing_speed", 0),
        session_duration=0,
        is_suspicious=risk_score >= 0.5,
        risk_score=risk_score,
        anomaly_score=anomaly_score,
        risk_factors=json.dumps(factors),
        login_success=success,
        is_new_device=any(r["factor"] == "New Device Detected" for r in factors),
        is_new_location=any(r["factor"] == "New Location Detected" for r in factors),
        is_unusual_time=any(r["factor"] == "Unusual Login Time" for r in factors),
        is_vpn=login_data.get("is_vpn", False),
    )

    db.session.add(activity)
    db.session.commit()
    return activity


def _hours_since_last_login(user):
    if user.last_login:
        return (datetime.utcnow() - user.last_login).total_seconds() / 3600
    return 24.0
