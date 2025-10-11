import pytest
from flask import url_for
from src.models.user import User
from src.services.auth_service import AuthService

class TestAuthRoutes:
    def test_login_route(self, test_client, init_database):
        # Test GET request to login page
        response = test_client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

        # Test successful login
        response = test_client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Logout' in response.data

        # Test failed login
        response = test_client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Login Unsuccessful' in response.data

    def test_logout_route(self, logged_in_client):
        # Test logout
        response = logged_in_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_register_route(self, test_client, init_database):
        # Test GET request to register page
        response = test_client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data

        # Test successful registration
        response = test_client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Your account has been created!' in response.data

        # Test duplicate username registration
        response = test_client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'new2@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Username already exists' in response.data

        # Test duplicate email registration
        response = test_client.post('/auth/register', data={
            'username': 'newuser2',
            'email': 'test@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Email already exists' in response.data

    def test_password_reset_route(self, test_client, init_database):
        # Test GET request to reset password page
        response = test_client.get('/auth/reset_password')
        assert response.status_code == 200
        assert b'Reset Password' in response.data

        # Test password reset request
        response = test_client.post('/auth/reset_password', data={
            'email': 'test@example.com'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'An email has been sent' in response.data

class TestAuthService:
    def test_register_user(self, init_database):
        # Test successful registration
        user, error = AuthService.register_user(
            username='serviceuser',
            email='service@example.com',
            password='servicepass123',
            first_name='Service',
            last_name='User'
        )
        assert user is not None
        assert error is None
        assert user.username == 'serviceuser'
        assert user.email == 'service@example.com'

        # Test duplicate username
        user, error = AuthService.register_user(
            username='testuser',
            email='service2@example.com',
            password='servicepass123'
        )
        assert user is None
        assert error == "Username or email already exists"

        # Test duplicate email
        user, error = AuthService.register_user(
            username='serviceuser2',
            email='test@example.com',
            password='servicepass123'
        )
        assert user is None
        assert error == "Username or email already exists"

    def test_authenticate_user(self, init_database):
        # Test successful authentication
        user = AuthService.authenticate_user('test@example.com', 'password123')
        assert user is not None
        assert user.email == 'test@example.com'

        # Test failed authentication - wrong password
        user = AuthService.authenticate_user('test@example.com', 'wrongpassword')
        assert user is None

        # Test failed authentication - wrong email
        user = AuthService.authenticate_user('wrong@example.com', 'password123')
        assert user is None

    def test_update_password(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()

        # Test successful password update
        success, error = AuthService.update_password(
            user.id,
            'password123',
            'newpassword123'
        )
        assert success is True
        assert error is None

        # Test wrong current password
        success, error = AuthService.update_password(
            user.id,
            'wrongpassword',
            'newpassword123'
        )
        assert success is False
        assert error == "Current password is incorrect"

        # Test non-existent user
        success, error = AuthService.update_password(
            9999,
            'password123',
            'newpassword123'
        )
        assert success is False
        assert error == "User not found"

    def test_reset_password(self, init_database):
        # Test password reset
        success, new_password = AuthService.reset_password('test@example.com')
        assert success is True
        assert len(new_password) == 12

        # Test non-existent user
        success, new_password = AuthService.reset_password('nonexistent@example.com')
        assert success is False
        assert new_password == "User not found"

    def test_update_user_profile(self, init_database):
        user = User.query.filter_by(email='test@example.com').first()

        # Test successful profile update
        success, error = AuthService.update_user_profile(
            user.id,
            first_name='Updated',
            last_name='User',
            phone_number='1234567890'
        )
        assert success is True
        assert error is None
        assert user.first_name == 'Updated'
        assert user.last_name == 'User'
        assert user.phone_number == '1234567890'

        # Test non-existent user
        success, error = AuthService.update_user_profile(
            9999,
            first_name='Updated'
        )
        assert success is False
        assert error == "User not found"