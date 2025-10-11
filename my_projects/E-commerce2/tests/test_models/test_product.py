import pytest
from datetime import datetime
from src.models.product import Product

class TestProductModel:
    """Test cases for the Product model"""

    def test_product_creation(self, init_database):
        """Test creating a new product"""
        product = Product(
            name='Test Product',
            description='Test product description',
            price=19.99,
            stock_quantity=10,
            category='Test',
            sku='TEST-001',
            is_active=True,
            is_featured=False,
            discount_percentage=0
        )
        init_database.session.add(product)
        init_database.session.commit()

        assert product.id is not None
        assert product.name == 'Test Product'
        assert product.description == 'Test product description'
        assert float(product.price) == 19.99
        assert product.stock_quantity == 10
        assert product.category == 'Test'
        assert product.sku == 'TEST-001'
        assert product.is_active is True
        assert product.is_featured is False
        assert product.discount_percentage == 0
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_get_current_price(self, init_database):
        """Test getting the current price with and without discount"""
        product = Product(
            name='Test Product',
            price=100.00,
            stock_quantity=10,
            discount_percentage=20
        )
        init_database.session.add(product)
        init_database.session.commit()

        assert product.get_current_price() == 80.00

        product.discount_percentage = 0
        assert product.get_current_price() == 100.00

    def test_is_in_stock(self, init_database):
        """Test checking if product is in stock"""
        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)
        init_database.session.commit()

        assert product.is_in_stock() is True

        product.stock_quantity = 0
        assert product.is_in_stock() is False

    def test_reduce_stock(self, init_database):
        """Test reducing product stock"""
        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)
        init_database.session.commit()

        assert product.reduce_stock(5) is True
        assert product.stock_quantity == 5

        assert product.reduce_stock(10) is False
        assert product.stock_quantity == 5

    def test_increase_stock(self, init_database):
        """Test increasing product stock"""
        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)
        init_database.session.commit()

        product.increase_stock(5)
        assert product.stock_quantity == 15

    def test_toggle_featured(self, init_database):
        """Test toggling featured status"""
        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10,
            is_featured=False
        )
        init_database.session.add(product)
        init_database.session.commit()

        product.toggle_featured()
        assert product.is_featured is True

        product.toggle_featured()
        assert product.is_featured is False

    def test_toggle_active(self, init_database):
        """Test toggling active status"""
        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10,
            is_active=True
        )
        init_database.session.add(product)
        init_database.session.commit()

        product.toggle_active()
        assert product.is_active is False

        product.toggle_active()
        assert product.is_active is True

    def test_product_repr(self, init_database):
        """Test the string representation of a product"""
        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)
        init_database.session.commit()

        assert repr(product) == '<Product Test Product>'

    def test_to_dict(self, init_database):
        """Test converting product to dictionary"""
        product = Product(
            name='Test Product',
            description='Test product description',
            price=19.99,
            stock_quantity=10,
            category='Test',
            sku='TEST-001',
            is_active=True,
            is_featured=False,
            discount_percentage=0
        )
        init_database.session.add(product)
        init_database.session.commit()

        product_dict = product.to_dict()
        assert product_dict['name'] == 'Test Product'
        assert product_dict['description'] == 'Test product description'
        assert float(product_dict['price']) == 19.99
        assert product_dict['stock_quantity'] == 10
        assert product_dict['category'] == 'Test'
        assert product_dict['sku'] == 'TEST-001'
        assert product_dict['is_active'] is True
        assert product_dict['is_featured'] is False
        assert product_dict['discount_percentage'] == 0

    def test_product_relationships(self, init_database):
        """Test product relationships with cart items and order items"""
        product = Product(
            name='Test Product',
            price=19.99,
            stock_quantity=10
        )
        init_database.session.add(product)
        init_database.session.commit()

        assert hasattr(product, 'cart_items')
        assert hasattr(product, 'order_items')
        assert product.cart_items == []
        assert product.order_items == []