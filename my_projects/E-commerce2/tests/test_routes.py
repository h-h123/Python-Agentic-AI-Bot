import pytest
from src import create_app, db
from src.models.user import User
from src.models.product import Product, Category
from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderStatus
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def authenticated_client(client):
    # Create a test user
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('password123'),
        first_name='Test',
        last_name='User',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()

    # Log in the user
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    return client

@pytest.fixture
def setup_test_data():
    # Create categories
    electronics = Category(name='Electronics', slug='electronics', description='Electronic devices')
    clothing = Category(name='Clothing', slug='clothing', description='Clothing items')

    # Create products
    phone = Product(
        name='Smartphone',
        description='Latest smartphone model',
        price=599.99,
        stock_quantity=10,
        sku='PHONE123',
        slug='smartphone',
        category=electronics
    )

    shirt = Product(
        name='T-Shirt',
        description='Cotton t-shirt',
        price=19.99,
        stock_quantity=20,
        sku='SHIRT456',
        slug='t-shirt',
        category=clothing
    )

    db.session.add_all([electronics, clothing, phone, shirt])
    db.session.commit()

    return {
        'categories': [electronics, clothing],
        'products': [phone, shirt]
    }

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Home' in response.data

def test_about_route(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About Us' in response.data

def test_contact_route(client):
    response = client.get('/contact')
    assert response.status_code == 200
    assert b'Contact Us' in response.data

def test_product_list_route(client, setup_test_data):
    response = client.get('/products')
    assert response.status_code == 200
    assert b'Smartphone' in response.data
    assert b'T-Shirt' in response.data

def test_product_detail_route(client, setup_test_data):
    product = setup_test_data['products'][0]
    response = client.get(f'/{product.slug}')
    assert response.status_code == 200
    assert product.name.encode() in response.data

def test_category_list_route(client, setup_test_data):
    response = client.get('/categories')
    assert response.status_code == 200
    assert b'Electronics' in response.data
    assert b'Clothing' in response.data

def test_category_detail_route(client, setup_test_data):
    category = setup_test_data['categories'][0]
    response = client.get(f'/category/{category.slug}')
    assert response.status_code == 200
    assert category.name.encode() in response.data

def test_add_to_cart_route_unauthenticated(client, setup_test_data):
    product = setup_test_data['products'][0]
    response = client.post(f'/add-to-cart/{product.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page' in response.data

def test_add_to_cart_route(authenticated_client, setup_test_data):
    product = setup_test_data['products'][0]
    response = authenticated_client.post(f'/add-to-cart/{product.id}', data={'quantity': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert b'has been added to your cart' in response.data

def test_view_cart_route_unauthenticated(client):
    response = client.get('/cart', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page' in response.data

def test_view_cart_route(authenticated_client, setup_test_data):
    product = setup_test_data['products'][0]
    authenticated_client.post(f'/add-to-cart/{product.id}', data={'quantity': 1}, follow_redirects=True)
    response = authenticated_client.get('/cart')
    assert response.status_code == 200
    assert b'Your Shopping Cart' in response.data
    assert product.name.encode() in response.data

def test_update_cart_item_route(authenticated_client, setup_test_data):
    product = setup_test_data['products'][0]
    authenticated_client.post(f'/add-to-cart/{product.id}', data={'quantity': 1}, follow_redirects=True)

    # Get the cart item ID
    cart = Cart.query.filter_by(user_id=1, is_active=True).first()
    cart_item = cart.items[0]

    response = authenticated_client.post(f'/cart/update/{cart_item.id}', data={'quantity': 2}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Cart updated successfully' in response.data

def test_remove_cart_item_route(authenticated_client, setup_test_data):
    product = setup_test_data['products'][0]
    authenticated_client.post(f'/add-to-cart/{product.id}', data={'quantity': 1}, follow_redirects=True)

    # Get the cart item ID
    cart = Cart.query.filter_by(user_id=1, is_active=True).first()
    cart_item = cart.items[0]

    response = authenticated_client.get(f'/cart/remove/{cart_item.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Item removed from your cart' in response.data

def test_clear_cart_route(authenticated_client, setup_test_data):
    product = setup_test_data['products'][0]
    authenticated_client.post(f'/add-to-cart/{product.id}', data={'quantity': 1}, follow_redirects=True)

    response = authenticated_client.get('/cart/clear', follow_redirects=True)
    assert response.status_code == 200
    assert b'Your cart has been cleared' in response.data

def test_checkout_route_unauthenticated(client):
    response = client.get('/checkout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page' in response.data

def test_checkout_route(authenticated_client, setup_test_data):
    product = setup_test_data['products'][0]
    authenticated_client.post(f'/add-to-cart/{product.id}', data={'quantity': 1}, follow_redirects=True)

    response = authenticated_client.get('/checkout')
    assert response.status_code == 200
    assert b'Checkout' in response.data

def test_order_list_route_unauthenticated(client):
    response = client.get('/orders', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page' in response.data

def test_order_list_route(authenticated_client):
    response = authenticated_client.get('/orders')
    assert response.status_code == 200
    assert b'Your Orders' in response.data

def test_register_route(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_login_route(client):
    response = client.get('/login')
    assert response_code == 200
    assert b'Login' in response.data

def test_logout_route(authenticated_client):
    response = authenticated_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_search_route(client, setup_test_data):
    response = client.get('/products?q=smart')
    assert response.status_code == 200
    assert b'Smartphone' in response.data

def test_404_route(client):
    response = client.get('/nonexistent-route')
    assert response.status_code == 404