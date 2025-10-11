from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from src.models.user import User
from src import db
from flask import current_app

class AuthService:
    @staticmethod
    def register_user(user_data):
        try:
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                return None, "Email already registered"

            existing_username = User.query.filter_by(username=user_data['username']).first()
            if existing_username:
                return None, "Username already taken"

            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                phone=user_data.get('phone', ''),
                address=user_data.get('address', '')
            )
            user.save()
            return user, None
        except Exception as e:
            current_app.logger.error(f"Error registering user: {str(e)}")
            db.session.rollback()
            return None, "An error occurred during registration"

    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            return user
        return None

    @staticmethod
    def login_user(user, remember=False):
        login_user(user, remember=remember)
        return True

    @staticmethod
    def logout_user():
        logout_user()
        return True

    @staticmethod
    def update_password(user_id, current_password, new_password):
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        if not user.verify_password(current_password):
            return False, "Current password is incorrect"

        try:
            user.password = new_password
            user.save()
            return True, None
        except Exception as e:
            current_app.logger.error(f"Error updating password: {str(e)}")
            db.session.rollback()
            return False, "An error occurred while updating password"

    @staticmethod
    def reset_password(email, new_password):
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "User not found"

        try:
            user.password = new_password
            user.save()
            return True, None
        except Exception as e:
            current_app.logger.error(f"Error resetting password: {str(e)}")
            db.session.rollback()
            return False, "An error occurred while resetting password"

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)