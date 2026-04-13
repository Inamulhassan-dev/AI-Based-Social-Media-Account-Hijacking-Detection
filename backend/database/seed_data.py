from app import app
from database.db import db
from models.user import User


def seed_admin():
    with app.app_context():
        if User.query.filter_by(username="admin").first():
            print("Admin already exists")
            return
        from flask_bcrypt import Bcrypt

        bcrypt = Bcrypt(app)
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="System Admin",
            password_hash=bcrypt.generate_password_hash("Admin@123").decode("utf-8"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin / Admin@123")


if __name__ == "__main__":
    seed_admin()
