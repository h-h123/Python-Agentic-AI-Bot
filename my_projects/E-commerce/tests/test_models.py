import unittest
from datetime import datetime
from decimal import Decimal
from app import create_app, db
from models.user import User, Address, Review
from models.product import Product, Category, ProductImage
from models.cart import Cart, CartItem
from models.order import Order, OrderItem, OrderStatus, PaymentStatus
from flask_login import current_user

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        self.user.set_password('password123')
        db.session.add(self.user)

        # Create test address
        self.address = Address(
            user_id=self.user.id,
            street='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country',
            is_default=True
        )
        db.session.add(self.address)

        # Create test category
        self.category = Category(
            name='Test Category',
            slug='test-category',
            description='Test category description',
            is_active=True
        )
        db.session.add(self.category)

        # Create test product
        self.product = Product(
            name='Test Product',
            description='Test product description',
            price=Decimal('19.99'),
            stock=100,
            sku='TEST123',
            category_id=self.category.id,
            is_active=True
        )
        db.session.add(self.product)

        # Create test cart
        self.cart = Cart(user_id=self.user.id)
        db.session.add(self.cart)

        # Create test cart item
        self.cart_item = CartItem(
            cart_id=self.cart.id,
            product_id=self.product.id,
            quantity=2
        )
        db.session.add(self.cart_item)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('password123'))
        self.assertFalse(self.user.check_password('wrongpassword'))
        self.assertEqual(self.user.get_full_name(), 'Test User')
        self.assertTrue(self.user.is_active_user())

    def test_address_model(self):
        self.assertEqual(self.address.street, '123 Test St')
        self.assertEqual(self.address.city, 'Test City')
        self.assertTrue(self.address.is_default)

    def test_category_model(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertTrue(self.category.is_active)

    def test_product_model(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, Decimal('19.99'))
        self.assertEqual(self.product.stock, 100)
        self.assertEqual(self.product.sku, 'TEST123')
        self.assertTrue(self.product.is_active)
        self.assertTrue(self.product.is_in_stock())
        self.assertEqual(self.product.get_current_price(), Decimal('19.99'))

    def test_cart_model(self):
        self.assertEqual(self.cart.user_id, self.user.id)
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.get_total_items(), 2)
        self.assertEqual(self.cart.get_total_price(), Decimal('39.98'))

    def test_cart_item_model(self):
        self.assertEqual(self.cart_item.cart_id, self.cart.id)
        self.assertEqual(self.cart_item.product_id, self.product.id)
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(self.cart_item.get_subtotal(), Decimal('39.98'))

    def test_cart_operations(self):
        # Test add_item
        product2 = Product(
            name='Test Product 2',
            price=Decimal('9.99'),
            stock=50,
            sku='TEST456',
            category_id=self.category.id,
            is_active=True
        )
        db.session.add(product2)
        db.session.commit()

        self.cart.add_item(product2, 3)
        self.assertEqual(len(self.cart.items), 2)
        self.assertEqual(self.cart.get_total_items(), 5)

        # Test update_item_quantity
        self.cart.update_item_quantity(product2, 5)
        self.assertEqual(self.cart.get_total_items(), 7)

        # Test remove_item
        self.cart.remove_item(product2)
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.get_total_items(), 2)

        # Test clear
        self.cart.clear()
        self.assertEqual(len(self.cart.items), 0)
        self.assertEqual(self.cart.get_total_items(), 0)

    def test_order_model(self):
        order = Order(
            user_id=self.user.id,
            order_number='ORD-20230101-123456',
            status=OrderStatus.PENDING,
            total_amount=Decimal('39.98'),
            shipping_address_id=self.address.id,
            payment_method='credit_card',
            payment_status=PaymentStatus.PENDING
        )
        db.session.add(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=self.product.id,
            product_name=self.product.name,
            product_sku=self.product.sku,
            quantity=2,
            unit_price=Decimal('19.99')
        )
        db.session.add(order_item)
        db.session.commit()

        self.assertEqual(order.user_id, self.user.id)
        self.assertEqual(order.order_number, 'ORD-20230101-123456')
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.payment_status, PaymentStatus.PENDING)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.get_order_items_count(), 2)

    def test_order_status_transitions(self):
        order = Order(
            user_id=self.user.id,
            order_number='ORD-20230101-123456',
            status=OrderStatus.PENDING,
            total_amount=Decimal('39.98'),
            shipping_address_id=self.address.id,
            payment_method='credit_card',
            payment_status=PaymentStatus.PENDING
        )
        db.session.add(order)
        db.session.commit()

        # Test status updates
        order.update_status(OrderStatus.PROCESSING)
        self.assertEqual(order.status, OrderStatus.PROCESSING)

        order.update_status('shipped')
        self.assertEqual(order.status, OrderStatus.SHIPPED)

        order.mark_as_completed()
        self.assertEqual(order.status, OrderStatus.DELIVERED)

        # Test payment status updates
        order.update_payment_status(PaymentStatus.COMPLETED)
        self.assertEqual(order.payment_status, PaymentStatus.COMPLETED)

    def test_review_model(self):
        review = Review(
            user_id=self.user.id,
            product_id=self.product.id,
            rating=5,
            comment='Great product!',
            is_approved=True
        )
        db.session.add(review)
        db.session.commit()

        self.assertEqual(review.user_id, self.user.id)
        self.assertEqual(review.product_id, self.product.id)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great product!')
        self.assertTrue(review.is_approved)

    def test_product_image_model(self):
        image = ProductImage(
            product_id=self.product.id,
            image_url='test-image.jpg',
            is_primary=True,
            alt_text='Test image',
            display_order=1
        )
        db.session.add(image)
        db.session.commit()

        self.assertEqual(image.product_id, self.product.id)
        self.assertEqual(image.image_url, 'test-image.jpg')
        self.assertTrue(image.is_primary)
        self.assertEqual(image.alt_text, 'Test image')
        self.assertEqual(image.display_order, 1)

if __name__ == '__main__':
    unittest.main()