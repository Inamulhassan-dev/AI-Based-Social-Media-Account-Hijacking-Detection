import json
from collections import deque
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.db import db
from models.alert import Alert
from services.alert_service import AlertService

alert_bp = Blueprint("alerts", __name__)

# Ephemeral live feed (in-memory). Keeps latest events for active demo UX.
LIVE_FEED = deque(maxlen=200)


def _risk_factors_for_scenario(scenario_name):
    scenarios = {
        "new_device": {
            "severity": "medium",
            "alert_type": "new_device",
            "title": "Login from New Device",
            "risk_score": 0.46,
            "factors": [
                {"factor": "New Device Detected", "detail": "Unseen browser fingerprint used"},
                {"factor": "Unusual Login Time", "detail": "Login occurred outside common active window"},
            ],
        },
        "impossible_travel": {
            "severity": "critical",
            "alert_type": "impossible_travel",
            "title": "Impossible Travel Detected",
            "risk_score": 0.91,
            "factors": [
                {"factor": "Impossible Travel Detected", "detail": "Dhaka to Berlin within 30 minutes"},
                {"factor": "New Location Detected", "detail": "First login from this geography"},
                {"factor": "VPN/Proxy Detected", "detail": "Connection appears proxied"},
            ],
        },
        "brute_force": {
            "severity": "high",
            "alert_type": "brute_force",
            "title": "Multiple Failed Login Attempts",
            "risk_score": 0.73,
            "factors": [
                {"factor": "Multiple Failed Attempts", "detail": "11 failed attempts in 3 minutes"},
                {"factor": "Abnormal Behavior", "detail": "Automation-like retry cadence detected"},
            ],
        },
        "bot_takeover": {
            "severity": "critical",
            "alert_type": "hijacking",
            "title": "Bot Takeover Pattern Detected",
            "risk_score": 0.95,
            "factors": [
                {"factor": "Abnormal Behavior", "detail": "Session interactions indicate scripted activity"},
                {"factor": "New Device Detected", "detail": "Unknown device with mismatched fingerprint"},
                {"factor": "VPN/Proxy Detected", "detail": "Traffic routed through high-risk proxy ASN"},
            ],
        },
    }
    return scenarios.get(scenario_name, scenarios["new_device"])


def _push_feed_event(user_id, alert):
    LIVE_FEED.appendleft(
        {
            "event_time": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "alert_id": alert.id,
            "title": alert.title,
            "severity": alert.severity,
            "risk_score": alert.risk_score,
            "status": "critical" if alert.risk_score >= 0.8 else ("high" if alert.risk_score >= 0.5 else ("warning" if alert.risk_score >= 0.3 else "normal")),
        }
    )


@alert_bp.route("/api/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    user_id = int(get_jwt_identity())
    unread_only = request.args.get("unread", "false").lower() == "true"
    alerts = AlertService.get_user_alerts(user_id, unread_only=unread_only)
    stats = AlertService.get_alert_stats(user_id)
    return jsonify({"alerts": alerts, "stats": stats}), 200


@alert_bp.route("/api/alerts/<int:alert_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(alert_id):
    user_id = int(get_jwt_identity())
    AlertService.mark_as_read(alert_id, user_id)
    return jsonify({"message": "Alert marked as read"}), 200


@alert_bp.route("/api/alerts/mark-all-read", methods=["PUT"])
@jwt_required()
def mark_all_read():
    user_id = int(get_jwt_identity())
    Alert.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "All alerts marked as read"}), 200


@alert_bp.route("/api/alerts/live-feed", methods=["GET"])
@jwt_required()
def get_live_feed():
    limit = request.args.get("limit", 20, type=int)
    return jsonify({"events": list(LIVE_FEED)[: max(1, min(limit, 100))]}), 200


@alert_bp.route("/api/alerts/demo-scenario", methods=["POST"])
@jwt_required()
def create_demo_scenario():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    scenario = data.get("scenario", "new_device")

    scenario_data = _risk_factors_for_scenario(scenario)
    factors = scenario_data["factors"]

    alert = Alert(
        user_id=user_id,
        activity_id=None,
        alert_type=scenario_data["alert_type"],
        severity=scenario_data["severity"],
        title=scenario_data["title"],
        message="\n".join([f"- {f['factor']}: {f['detail']}" for f in factors]),
        details=json.dumps(factors),
        risk_score=scenario_data["risk_score"],
    )
    db.session.add(alert)
    db.session.commit()

    _push_feed_event(user_id, alert)

    return jsonify({"message": "Demo scenario created", "alert": alert.to_dict()}), 201


@alert_bp.route("/api/alerts/<int:alert_id>/action", methods=["POST"])
@jwt_required()
def take_alert_action(alert_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    action = data.get("action", "reviewed")

    alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
    if not alert:
        return jsonify({"error": "Alert not found"}), 404

    action_map = {
        "this_was_me": "User confirmed activity as legitimate",
        "not_me": "User reported potential takeover",
        "lock_account": "Account locked by user action",
        "require_2fa": "2FA challenge requested for next login",
        "end_sessions": "Active sessions termination requested",
    }

    action_text = action_map.get(action, "Reviewed by user")
    alert.action_taken = action_text
    alert.is_read = True

    if action in {"this_was_me", "not_me"}:
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = f"user:{user_id}"

    db.session.commit()

    LIVE_FEED.appendleft(
        {
            "event_time": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "alert_id": alert.id,
            "title": f"Action taken: {action}",
            "severity": alert.severity,
            "risk_score": alert.risk_score,
            "status": "normal" if action == "this_was_me" else "warning",
        }
    )

    return jsonify({"message": "Action recorded", "alert": alert.to_dict()}), 200


@alert_bp.route("/api/alerts/security-score", methods=["GET"])
@jwt_required()
def get_security_score():
    user_id = int(get_jwt_identity())

    stats = AlertService.get_alert_stats(user_id)
    total = max(1, stats["total"])
    penalty = (stats["critical"] * 22) + (stats["high"] * 12) + (stats["unread"] * 4)
    score = max(0, min(100, 100 - penalty))

    tips = [
        "Enable 2FA for high-risk sessions",
        "Review unknown devices and revoke old sessions",
        "Rotate password every 60-90 days",
    ]

    return jsonify(
        {
            "security_score": score,
            "weekly_trend": [
                {"week": "W-4", "score": max(0, min(100, score - 6))},
                {"week": "W-3", "score": max(0, min(100, score - 3))},
                {"week": "W-2", "score": max(0, min(100, score - 2))},
                {"week": "W-1", "score": max(0, min(100, score - 1))},
                {"week": "Now", "score": score},
            ],
            "tips": tips,
        }
    ), 200
