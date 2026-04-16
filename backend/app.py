import logging
import os

from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_socketio import SocketIO

from config import Config
from database.db import init_db
from utils.jwt_handler import init_jwt

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

socketio = SocketIO(cors_allowed_origins="*")
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import models before init_db so create_all can discover all tables.
    import models  # noqa: F401

    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})
    bcrypt.init_app(app)
    init_db(app)
    init_jwt(app)
    socketio.init_app(app, cors_allowed_origins=app.config["FRONTEND_ORIGIN"])

    from routes.admin_routes import admin_bp
    from routes.analysis_routes import analysis_bp
    from routes.alert_routes import alert_bp
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(analysis_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "message": "AI Hijacking Detection API is running"}), 200

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "Internal server error"}), 500

    @socketio.on("connect")
    def handle_connect():
        logger.info("Client connected via WebSocket")

    @socketio.on("disconnect")
    def handle_disconnect():
        logger.info("Client disconnected")

    return app


app = create_app()


if __name__ == "__main__":
    _model_check = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml", "saved_models", "random_forest.pkl")
    if not os.path.exists(_model_check):
        logger.info("Training ML models for first time...")
        os.makedirs("data", exist_ok=True)
        from ml.generate_dataset import generate_dataset
        from ml.train_model import train_all_models

        generate_dataset()
        train_all_models()

    logger.info("Starting AI Hijacking Detection Server...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
