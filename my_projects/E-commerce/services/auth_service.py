from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_login import UserMixin
from ..models.user import User
from .. import db
import re
from datetime import datetime, timedelta

class AuthService:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        self.app = app

    def register_user(self, username, email, password, first_name=None, last_name=None, phone_number=None):
        """Register a new user"""
        if User.query.filter_by(email=email).first():
            return None, "Email already registered"

        if User.query.filter_by(username=username).first():
            return None, "Username already taken"

        if not self._is_valid_email(email):
            return None, "Invalid email format"

        if not self._is_valid_password(password):
            return None, "Password must be at least 8 characters long and contain at least one number and one letter"

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return user, None

    def authenticate_user(self, email, password):
        """Authenticate a user"""
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user

        return None

    def generate_password_reset_token(self, email):
        """Generate a password reset token"""
        user = User.query.filter_by(email=email).first()
        if user:
            return self.serializer.dumps(email, salt='password-reset-salt')
        return None

    def verify_password_reset_token(self, token, expiration=3600):
        """Verify a password reset token"""
        try:
            email = self.serializer.loads(
                token,
                salt='password-reset-salt',
                max_age=expiration
            )
        except:
            return None
        return User.query.filter_by(email=email).first()

    def reset_password(self, user, new_password):
        """Reset a user's password"""
        if not self._is_valid_password(new_password):
            return False, "Password must be at least 8 characters long and contain at least one number and one letter"

        user.set_password(new_password)
        db.session.commit()
        return True, None

    def change_password(self, user, current_password, new_password):
        """Change a user's password"""
        if not user.check_password(current_password):
            return False, "Current password is incorrect"

        if not self._is_valid_password(new_password):
            return False, "Password must be at least 8 characters long and contain at least one number and one letter"

        user.set_password(new_password)
        db.session.commit()
        return True, None

    def update_user_profile(self, user, **kwargs):
        """Update user profile information"""
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['id', 'password_hash', 'created_at', 'updated_at']:
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user

    def _is_valid_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _is_valid_password(self, password):
        """Validate password strength"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Za-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        return True

    def generate_email_confirmation_token(self, email):
        """Generate email confirmation token"""
        return self.serializer.dumps(email, salt='email-confirmation-salt')

    def confirm_email(self, token, expiration=86400):
        """Confirm user email with token"""
        try:
            email = self.serializer.loads(
                token,
                salt='email-confirmation-salt',
                max_age=expiration
            )
        except:
            return None

        user = User.query.filter_by(email=email).first()
        if user:
            user.email_confirmed = True
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return user
        return None

    def deactivate_user(self, user_id):
        """Deactivate a user account"""
        user = User.query.get(user_id)
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def reactivate_user(self, user_id):
        """Reactivate a user account"""
        user = User.query.get(user_id)
        if user:
            user.is_active = True
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def promote_to_admin(self, user_id):
        """Promote user to admin"""
        user = User.query.get(user_id)
        if user:
            user.is_admin = True
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def demote_from_admin(self, user_id):
        """Demote admin to regular user"""
        user = User.query.get(user_id)
        if user:
            user.is_admin = False
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False