from src.extensions import db, bcrypt
from src.models.user import User
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import string

class AuthService:
    @staticmethod
    def register_user(username, email, password, first_name=None, last_name=None):
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return None, "Username or email already exists"

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()
        return user, None

    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def update_password(user_id, current_password, new_password):
        user = User.get_by_id(user_id)
        if not user:
            return False, "User not found"

        if not bcrypt.check_password_hash(user.password_hash, current_password):
            return False, "Current password is incorrect"

        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.save()
        return True, None

    @staticmethod
    def reset_password(email):
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "User not found"

        # Generate a random password
        alphabet = string.ascii_letters + string.digits
        new_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.save()
        return True, new_password

    @staticmethod
    def update_user_profile(user_id, **kwargs):
        user = User.get_by_id(user_id)
        if not user:
            return False, "User not found"

        valid_fields = ['username', 'email', 'first_name', 'last_name',
                       'phone_number', 'shipping_address', 'billing_address']

        for field, value in kwargs.items():
            if field in valid_fields and value is not None:
                setattr(user, field, value)

        user.save()
        return True, None

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_id(user_id):
        return User.get_by_id(user_id)

    @staticmethod
    def generate_reset_token(email):
        user = User.query.filter_by(email=email).first()
        if not user:
            return None

        # Generate a token (in a real app, this would be a JWT or similar)
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
        user.save()
        return token

    @staticmethod
    def verify_reset_token(token):
        user = User.query.filter_by(reset_token=token).first()
        if not user or user.reset_token_expiration < datetime.utcnow():
            return None
        return user