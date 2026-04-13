from datetime import timedelta

from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token

jwt = JWTManager()


def init_jwt(app):
    jwt.init_app(app)
    return jwt


def generate_tokens(user_id, role="user"):
    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={"role": role},
        expires_delta=timedelta(hours=1),
    )
    refresh_token = create_refresh_token(identity=str(user_id), expires_delta=timedelta(days=30))
    return access_token, refresh_token
