import pytest
from datetime import datetime
from decimal import Decimal
from src.models.user import User
from src.models.product import Product, Category
from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderItem, OrderStatus
from src import db

class TestUserModel:
    def test_user_creation(self, session):
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.verify_password('password123') is True
        assert user.get_full_name() == 'Test User'

    def test_user_password_hashing(self, session):
        user = User(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        assert user.password_hash is not None
        assert user.password_hash != 'password123'
        assert user.verify_password('password123') is True
        assert user.verify_password('wrongpassword') is False

    def test_user_relationships(self, session):
        user = User(
            username='testuser3',
            email='test3@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        assert user.carts[0].id == cart.id
        assert cart.user_id == user.id

class TestProductModel:
    def test_product_creation(self, session):
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Test Product',
            description='Test Description',
            price=Decimal('19.99'),
            stock_quantity=10,
            sku='TEST123',
            slug='test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        assert product.id is not None
        assert product.name == 'Test Product'
        assert product.price == Decimal('19.99')
        assert product.stock_quantity == 10
        assert product.category_id == category.id

    def test_product_stock_management(self, session):
        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock_quantity=10,
            sku='TEST123',
            slug='test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        assert product.is_in_stock() is True
        assert product.decrease_stock(5) is True
        assert product.stock_quantity == 5
        assert product.increase_stock(3) is True
        assert product.stock_quantity == 8
        assert product.decrease_stock(10) is False

class TestCartModel:
    def test_cart_creation(self, session):
        user = User(
            username='cartuser',
            email='cart@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        assert cart.id is not None
        assert cart.user_id == user.id
        assert cart.is_active is True

    def test_cart_item_management(self, session):
        user = User(
            username='cartuser2',
            email='cart2@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock_quantity=10,
            sku='TEST123',
            slug='test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        # Add item to cart
        cart_item = cart.add_item(product, 2)
        assert cart_item.quantity == 2
        assert cart_item.unit_price == Decimal('19.99')
        assert cart.get_total_items() == 2
        assert cart.get_total_price() == Decimal('39.98')

        # Update item quantity
        updated_item = cart.update_item_quantity(product.id, 3)
        assert updated_item.quantity == 3
        assert cart.get_total_items() == 3
        assert cart.get_total_price() == Decimal('59.97')

        # Remove item
        removed_item = cart.remove_item(product.id)
        assert removed_item.product_id == product.id
        assert cart.get_total_items() == 0
        assert cart.get_total_price() == Decimal('0.00')

    def test_cart_clear(self, session):
        user = User(
            username='cartuser3',
            email='cart3@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock_quantity=10,
            sku='TEST123',
            slug='test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        cart.add_item(product, 2)
        cart.clear()

        assert cart.is_active is False
        assert len(cart.items) == 0

class TestOrderModel:
    def test_order_creation(self, session):
        user = User(
            username='orderuser',
            email='order@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        order = Order(
            user_id=user.id,
            order_number='ORD12345',
            shipping_address='123 Test St',
            billing_address='123 Test St',
            payment_method='credit_card',
            status=OrderStatus.PENDING,
            total_amount=Decimal('100.00')
        )
        session.add(order)
        session.commit()

        assert order.id is not None
        assert order.user_id == user.id
        assert order.order_number == 'ORD12345'
        assert order.status == OrderStatus.PENDING

    def test_order_status_updates(self, session):
        user = User(
            username='orderuser2',
            email='order2@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        order = Order(
            user_id=user.id,
            order_number='ORD67890',
            shipping_address='123 Test St',
            billing_address='123 Test St',
            payment_method='credit_card',
            status=OrderStatus.PENDING,
            total_amount=Decimal('100.00')
        )
        session.add(order)
        session.commit()

        order.update_status(OrderStatus.PROCESSING)
        assert order.status == OrderStatus.PROCESSING

        order.cancel()
        assert order.status == OrderStatus.CANCELLED

    def test_order_item_management(self, session):
        user = User(
            username='orderuser3',
            email='order3@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock_quantity=10,
            sku='TEST123',
            slug='test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        order = Order(
            user_id=user.id,
            order_number='ORD54321',
            shipping_address='123 Test St',
            billing_address='123 Test St',
            payment_method='credit_card',
            status=OrderStatus.PENDING,
            total_amount=Decimal('0.00')
        )
        session.add(order)
        session.commit()

        # Add item to order
        order_item = order.add_item(product, 2, Decimal('19.99'))
        assert order_item.quantity == 2
        assert order_item.unit_price == Decimal('19.99')
        assert order.calculate_total() == Decimal('39.98')

        # Verify product stock was decreased
        assert product.stock_quantity == 8

    def test_order_cancellation_stock_restore(self, session):
        user = User(
            username='orderuser4',
            email='order4@example.com',
            password='password123'
        )
        session.add(user)
        session.commit()

        category = Category(name='Test Category', slug='test-category')
        session.add(category)
        session.commit()

        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock_quantity=10,
            sku='TEST123',
            slug='test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        order = Order(
            user_id=user.id,
            order_number='ORD98765',
            shipping_address='123 Test St',
            billing_address='123 Test St',
            payment_method='credit_card',
            status=OrderStatus.PENDING,
            total_amount=Decimal('0.00')
        )
        session.add(order)
        session.commit()

        # Add item to order
        order.add_item(product, 3, Decimal('19.99'))
        assert product.stock_quantity == 7

        # Cancel order and verify stock is restored
        order.cancel()
        assert product.stock_quantity == 10
        assert order.status == OrderStatus.CANCELLED

class TestCategoryModel:
    def test_category_creation(self, session):
        category = Category(
            name='Test Category',
            slug='test-category',
            description='Test Description'
        )
        session.add(category)
        session.commit()

        assert category.id is not None
        assert category.name == 'Test Category'
        assert category.slug == 'test-category'

    def test_category_product_relationship(self, session):
        category = Category(
            name='Test Category',
            slug='test-category'
        )
        session.add(category)
        session.commit()

        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock_quantity=10,
            sku='TEST123',
            slug='test-product',
            category_id=category.id
        )
        session.add(product)
        session.commit()

        assert len(category.products) == 1
        assert category.products[0].id == product.id
        assert product.category_id == category.id