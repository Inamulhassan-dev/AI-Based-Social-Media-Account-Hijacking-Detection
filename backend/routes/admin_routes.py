from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from sqlalchemy import func

from models.alert import Alert
from models.login_activity import LoginActivity
from models.user import User
from services.alert_service import AlertService

admin_bp = Blueprint("admin", __name__)


def admin_required():
    claims = get_jwt()
    return claims.get("role") == "admin"


@admin_bp.route("/api/admin/stats", methods=["GET"])
@jwt_required()
def get_admin_stats():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    locked_users = User.query.filter_by(is_locked=True).count()

    today = datetime.utcnow().date()
    today_logins = LoginActivity.query.filter(func.date(LoginActivity.login_time) == today).count()
    today_suspicious = LoginActivity.query.filter(
        func.date(LoginActivity.login_time) == today, LoginActivity.is_suspicious.is_(True)
    ).count()

    total_alerts = Alert.query.count()
    unresolved_alerts = Alert.query.filter_by(is_resolved=False).count()
    critical_alerts = Alert.query.filter_by(severity="critical", is_resolved=False).count()

    login_trend = []
    for index in range(7):
        day = today - timedelta(days=index)
        count = LoginActivity.query.filter(func.date(LoginActivity.login_time) == day).count()
        suspicious = LoginActivity.query.filter(
            func.date(LoginActivity.login_time) == day, LoginActivity.is_suspicious.is_(True)
        ).count()
        login_trend.append({"date": day.isoformat(), "total": count, "suspicious": suspicious})

    return (
        jsonify(
            {
                "total_users": total_users,
                "active_users": active_users,
                "locked_users": locked_users,
                "today_logins": today_logins,
                "today_suspicious": today_suspicious,
                "total_alerts": total_alerts,
                "unresolved_alerts": unresolved_alerts,
                "critical_alerts": critical_alerts,
                "login_trend": login_trend[::-1],
            }
        ),
        200,
    )


@admin_bp.route("/api/admin/users", methods=["GET"])
@jwt_required()
def get_all_users():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]}), 200


@admin_bp.route("/api/admin/alerts", methods=["GET"])
@jwt_required()
def get_all_alerts():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(100).all()
    return jsonify({"alerts": [alert.to_dict() for alert in alerts]}), 200


@admin_bp.route("/api/admin/resolve-alert/<int:alert_id>", methods=["POST"])
@jwt_required()
def resolve_alert(alert_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json() or {}
    claims = get_jwt()
    action = data.get("action_taken", "Reviewed and resolved")

    success = AlertService.resolve_alert(alert_id, str(claims.get("sub")), action)
    if success:
        return jsonify({"message": "Alert resolved"}), 200
    return jsonify({"error": "Alert not found"}), 404


@admin_bp.route("/api/admin/model-performance", methods=["GET"])
@jwt_required()
def get_model_performance():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    import json
    import os

    results_path = os.path.join("ml", "saved_models", "training_results.json")
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as file:
            results = json.load(file)
        return jsonify({"model_performance": results}), 200

    return jsonify({"model_performance": {}}), 200
