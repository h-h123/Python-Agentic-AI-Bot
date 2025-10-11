import pytest
from src import create_app, db
from src.models.user import User
from src.models.product import Product
from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderItem
from config.settings import TestingConfig
from flask_login import login_user

@pytest.fixture(scope='module')
def test_app():
    """Create and configure a new app instance for testing"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    """A test client for the app"""
    return test_app.test_client()

@pytest.fixture(scope='module')
def init_database(test_app):
    """Initialize the database with test data"""
    with test_app.app_context():
        # Create test users
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('test123')
        db.session.add(user)

        # Create test products
        product1 = Product(
            name='Test Product 1',
            description='Test product description 1',
            price=19.99,
            stock_quantity=10,
            category='Test'
        )
        db.session.add(product1)

        product2 = Product(
            name='Test Product 2',
            description='Test product description 2',
            price=29.99,
            stock_quantity=5,
            category='Test'
        )
        db.session.add(product2)

        db.session.commit()

        yield db

        # Clean up
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def logged_in_client(test_client, init_database):
    """Create a client with a logged-in user"""
    with test_client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        with test_client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['_fresh'] = True

        login_user(user)
        yield test_client

@pytest.fixture(scope='function')
def admin_client(test_client, init_database):
    """Create a client with a logged-in admin user"""
    with test_client.application.app_context():
        user = User.query.filter_by(email='admin@example.com').first()
        with test_client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['_fresh'] = True

        login_user(user)
        yield test_client

@pytest.fixture(scope='function')
def test_cart(init_database):
    """Create a test cart with items"""
    with init_database.app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        product1 = Product.query.filter_by(name='Test Product 1').first()
        product2 = Product.query.filter_by(name='Test Product 2').first()

        cart = Cart(user_id=user.id)
        db.session.add(cart)

        cart_item1 = CartItem(
            cart_id=cart.id,
            product_id=product1.id,
            quantity=2
        )
        db.session.add(cart_item1)

        cart_item2 = CartItem(
            cart_id=cart.id,
            product_id=product2.id,
            quantity=1
        )
        db.session.add(cart_item2)

        db.session.commit()
        yield cart

@pytest.fixture(scope='function')
def test_order(init_database):
    """Create a test order with items"""
    with init_database.app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        product1 = Product.query.filter_by(name='Test Product 1').first()
        product2 = Product.query.filter_by(name='Test Product 2').first()

        order = Order(
            user_id=user.id,
            shipping_address='123 Test St, Test City',
            total_amount=69.97,
            shipping_amount=5.00,
            tax_amount=4.00
        )
        db.session.add(order)

        order_item1 = OrderItem(
            order_id=order.id,
            product_id=product1.id,
            quantity=2,
            unit_price=19.99
        )
        db.session.add(order_item1)

        order_item2 = OrderItem(
            order_id=order.id,
            product_id=product2.id,
            quantity=1,
            unit_price=29.99
        )
        db.session.add(order_item2)

        db.session.commit()
        yield order