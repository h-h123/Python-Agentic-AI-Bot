import pytest
from src import create_app, db
from src.models import User, Product, Cart, Order, OrderItem, ProductCategory, CartItem
from config.config import TestingConfig
import os
import tempfile

@pytest.fixture(scope='module')
def test_app():
    app = create_app('testing')

    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='module')
def init_database(test_app):
    with test_app.app_context():
        # Create test admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # Create test regular user
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password123')
        db.session.add(user)

        # Create test category
        category = ProductCategory(
            name='Electronics',
            description='Electronic devices'
        )
        db.session.add(category)

        # Create test product
        product = Product(
            name='Test Product',
            description='Test product description',
            price=9.99,
            stock=100,
            category_id=category.id,
            sku='TEST001'
        )
        db.session.add(product)

        db.session.commit()

        yield db

        db.session.remove()
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
        name='Smartphone',
        description='Latest smartphone model',
        price=599.99,
        stock=50,
        category_id=category.id,
        sku='PHONE001'
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
def test_cart_with_items(test_cart, test_product):
    cart_item = CartItem(
        cart_id=test_cart.id,
        product_id=test_product.id,
        quantity=2
    )
    cart_item.save()
    return test_cart

@pytest.fixture(scope='function')
def test_order(init_database, logged_in_client):
    user = User.query.filter_by(email='test@example.com').first()
    product = Product.query.first()

    order = Order(
        user_id=user.id,
        order_number='TEST12345',
        shipping_address='123 Test St, Test City',
        billing_address='123 Test St, Test City',
        payment_method='credit_card',
        total_amount=9.99,
        status='Pending'
    )
    order.save()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=1,
        price=9.99
    )
    order_item.save()

    return order

@pytest.fixture(scope='function')
def runner(test_app):
    return test_app.test_cli_runner()