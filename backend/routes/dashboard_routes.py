from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.login_activity import LoginActivity
from models.user import User
from services.alert_service import AlertService
from services.behavior_analyzer import BehaviorAnalyzer

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/summary", methods=["GET"])
@jwt_required()
def get_dashboard_summary():
    user_id = int(get_jwt_identity())
    behavior = BehaviorAnalyzer.get_behavior_summary(user_id)
    alert_stats = AlertService.get_alert_stats(user_id)
    user = User.query.get(user_id)
    return jsonify({"user": user.to_dict() if user else {}, "behavior": behavior, "alert_stats": alert_stats}), 200


@dashboard_bp.route("/api/dashboard/activities", methods=["GET"])
@jwt_required()
def get_activities():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    activities = (
        LoginActivity.query.filter_by(user_id=user_id)
        .order_by(LoginActivity.login_time.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return (
        jsonify(
            {
                "activities": [a.to_dict() for a in activities.items],
                "total": activities.total,
                "pages": activities.pages,
                "current_page": page,
            }
        ),
        200,
    )


@dashboard_bp.route("/api/dashboard/risk-history", methods=["GET"])
@jwt_required()
def get_risk_history():
    user_id = int(get_jwt_identity())

    activities = LoginActivity.query.filter_by(user_id=user_id).order_by(LoginActivity.login_time.desc()).limit(100).all()

    history = [
        {
            "date": a.login_time.isoformat(),
            "risk_score": a.risk_score,
            "is_suspicious": a.is_suspicious,
            "country": a.country,
        }
        for a in activities
    ]

    return jsonify({"risk_history": history}), 200
