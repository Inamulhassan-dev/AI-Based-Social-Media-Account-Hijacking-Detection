from flask import Blueprint, jsonify

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/api/analysis/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"}), 200
