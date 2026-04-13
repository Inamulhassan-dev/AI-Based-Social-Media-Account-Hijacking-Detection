from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.social_threat_service import SocialThreatService

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/api/analysis/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"}), 200


@analysis_bp.route("/api/analysis/social-insights", methods=["GET"])
@jwt_required()
def social_insights():
    user_id = int(get_jwt_identity())
    insights = SocialThreatService.get_social_insights(user_id)
    return jsonify({"social_insights": insights}), 200
