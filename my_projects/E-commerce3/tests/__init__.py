# tests/__init__.py

import pytest
from src import create_app, db
from src.models import User, Product, Cart, Order, OrderItem, ProductCategory
from config.config import TestingConfig

@pytest.fixture(scope='module')
def test_app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='module')
def init_database(test_app):
    db.create_all()

    # Create test data
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash='pbkdf2:sha256:150000$test$test',
        is_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)

    user = User(
        username='testuser',
        email='test@example.com',
        password_hash='pbkdf2:sha256:150000$test$test'
    )
    user.set_password('password123')
    db.session.add(user)

    category = ProductCategory(name='Test Category', description='Test Description')
    db.session.add(category)

    product = Product(
        name='Test Product',
        description='Test Description',
        price=10.99,
        stock=100,
        category_id=category.id
    )
    db.session.add(product)

    db.session.commit()

    yield db

    db.drop_all()

@pytest.fixture(scope='function')
def logged_in_client(test_client, init_database):
    test_client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    return test_client

@pytest.fixture(scope='function')
def admin_client(test_client, init_database):
    test_client.post('/auth/login', data={
        'email': 'admin@example.com',
        'password': 'admin123'
    }, follow_redirects=True)
    return test_client

@pytest.fixture(scope='function')
def test_product(init_database):
    category = ProductCategory.query.first()
    product = Product(
        name='Test Product 2',
        description='Another test product',
        price=19.99,
        stock=50,
        category_id=category.id
    )
    product.save()
    return product

@pytest.fixture(scope='function')
def test_cart(init_database, logged_in_client):
    user = User.query.filter_by(email='test@example.com').first()
    cart = Cart(user_id=user.id)
    cart.save()
    return cart

@pytest.fixture(scope='function')
def test_order(init_database, logged_in_client):
    user = User.query.filter_by(email='test@example.com').first()
    product = Product.query.first()

    order = Order(
        user_id=user.id,
        order_number='TEST12345',
        shipping_address='123 Test St',
        payment_method='credit_card',
        total_amount=10.99
    )
    order.save()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=1,
        price=10.99
    )
    order_item.save()

    return order