from flask_testing import TestCase
from flask import current_app
import unittest

class BaseTestCase(TestCase):
    """Base test case for the e-commerce application."""

    def create_app(self):
        """Create and configure the test application."""
        from app import app
        app.config.from_object('config.TestingConfig')
        return app

    def setUp(self):
        """Set up test fixtures."""
        db = current_app.extensions['sqlalchemy'].db
        db.create_all()

    def tearDown(self):
        """Tear down test fixtures."""
        db = current_app.extensions['sqlalchemy'].db
        db.session.remove()
        db.drop_all()

if __name__ == '__main__':
    unittest.main()