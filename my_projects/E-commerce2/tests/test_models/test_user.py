import pytest
from datetime import datetime
from werkzeug.security import check_password_hash
from src.models.user import User

class TestUserModel:
    """Test cases for the User model"""

    def test_user_creation(self, init_database):
        """Test creating a new user"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password_hash='testpassword'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.is_active is True
        assert user.is_admin is False
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_password_hashing(self, init_database):
        """Test password hashing and verification"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        assert check_password_hash(user.password_hash, 'testpassword') is True
        assert check_password_hash(user.password_hash, 'wrongpassword') is False

    def test_user_repr(self, init_database):
        """Test the string representation of a user"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        assert repr(user) == '<User testuser>'

    def test_get_full_name(self, init_database):
        """Test getting the full name of a user"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        assert user.get_full_name() == 'Test User'

        user.first_name = None
        user.last_name = None
        assert user.get_full_name() == 'testuser'

    def test_update_last_login(self, init_database):
        """Test updating the last login timestamp"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        old_login = user.last_login
        user.update_last_login()

        assert user.last_login is not None
        assert user.last_login != old_login

    def test_deactivate_activate_user(self, init_database):
        """Test deactivating and activating a user"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        assert user.is_active is True

        user.deactivate()
        assert user.is_active is False

        user.activate()
        assert user.is_active is True

    def test_has_active_cart(self, init_database):
        """Test checking if user has an active cart"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        assert user.has_active_cart() is False

    def test_to_dict(self, init_database):
        """Test converting user to dictionary"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone_number='1234567890',
            shipping_address='123 Test St',
            billing_address='123 Test St'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        user_dict = user.to_dict()
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['first_name'] == 'Test'
        assert user_dict['last_name'] == 'User'
        assert user_dict['phone_number'] == '1234567890'
        assert user_dict['shipping_address'] == '123 Test St'
        assert user_dict['billing_address'] == '123 Test St'
        assert 'password_hash' not in user_dict

    def test_user_relationships(self, init_database):
        """Test user relationships with carts and orders"""
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword')
        init_database.session.add(user)
        init_database.session.commit()

        assert hasattr(user, 'carts')
        assert hasattr(user, 'orders')
        assert user.carts == []
        assert user.orders == []