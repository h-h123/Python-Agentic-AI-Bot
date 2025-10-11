import pytest
from flask import url_for
from src.models.product import Product
from src.models.user import User

class TestProductRoutes:
    """Test cases for product routes"""

    def test_product_list_route(self, test_client, init_database):
        """Test the product list route"""
        response = test_client.get('/products/')
        assert response.status_code == 200
        assert b'Products' in response.data

    def test_product_detail_route(self, test_client, init_database):
        """Test the product detail route"""
        product = Product.query.first()
        response = test_client.get(f'/products/{product.id}')
        assert response.status_code == 200
        assert product.name.encode() in response.data

    def test_product_detail_route_not_found(self, test_client, init_database):
        """Test the product detail route with non-existent product"""
        response = test_client.get('/products/999999')
        assert response.status_code == 404

    def test_add_to_cart_route_unauthenticated(self, test_client, init_database):
        """Test add to cart route without authentication"""
        product = Product.query.first()
        response = test_client.post(f'/products/{product.id}/add_to_cart', data={'quantity': 1})
        assert response.status_code == 302  # Redirect to login

    def test_add_to_cart_route_authenticated(self, logged_in_client, init_database):
        """Test add to cart route with authentication"""
        product = Product.query.first()
        response = logged_in_client.post(f'/products/{product.id}/add_to_cart', data={'quantity': 1}, follow_redirects=True)
        assert response.status_code == 200
        assert b'added to cart successfully' in response.data

    def test_add_to_cart_route_invalid_quantity(self, logged_in_client, init_database):
        """Test add to cart route with invalid quantity"""
        product = Product.query.first()
        response = logged_in_client.post(f'/products/{product.id}/add_to_cart', data={'quantity': 0}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Quantity must be greater than 0' in response.data

    def test_add_to_cart_route_out_of_stock(self, logged_in_client, init_database):
        """Test add to cart route with out of stock product"""
        product = Product.query.first()
        product.stock_quantity = 0
        init_database.session.commit()

        response = logged_in_client.post(f'/products/{product.id}/add_to_cart', data={'quantity': 1}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Product is out of stock' in response.data

    def test_featured_products_route(self, test_client, init_database):
        """Test the featured products route"""
        response = test_client.get('/products/featured')
        assert response.status_code == 200
        assert b'Featured Products' in response.data

    def test_products_by_category_route(self, test_client, init_database):
        """Test the products by category route"""
        product = Product.query.first()
        response = test_client.get(f'/products/category/{product.category}')
        assert response.status_code == 200
        assert product.category.encode() in response.data

    def test_admin_product_list_route_unauthorized(self, test_client, init_database):
        """Test admin product list route without admin privileges"""
        response = test_client.get('/products/admin')
        assert response.status_code == 302  # Redirect to login

    def test_admin_product_list_route_authorized(self, admin_client, init_database):
        """Test admin product list route with admin privileges"""
        response = admin_client.get('/products/admin')
        assert response.status_code == 200
        assert b'Product Management' in response.data

    def test_admin_create_product_route_get(self, admin_client, init_database):
        """Test GET request to admin create product route"""
        response = admin_client.get('/products/admin/create')
        assert response.status_code == 200
        assert b'Create New Product' in response.data

    def test_admin_create_product_route_post(self, admin_client, init_database):
        """Test POST request to admin create product route"""
        response = admin_client.post('/products/admin/create', data={
            'name': 'New Test Product',
            'description': 'New test product description',
            'price': 29.99,
            'stock_quantity': 15,
            'category': 'Test',
            'sku': 'TEST-003',
            'is_featured': 'y'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Product created successfully' in response.data

        # Verify product was created
        product = Product.query.filter_by(name='New Test Product').first()
        assert product is not None
        assert product.price == 29.99
        assert product.stock_quantity == 15
        assert product.is_featured is True

    def test_admin_edit_product_route_get(self, admin_client, init_database):
        """Test GET request to admin edit product route"""
        product = Product.query.first()
        response = admin_client.get(f'/products/admin/{product.id}/edit')
        assert response.status_code == 200
        assert b'Edit Product' in response.data

    def test_admin_edit_product_route_post(self, admin_client, init_database):
        """Test POST request to admin edit product route"""
        product = Product.query.first()
        response = admin_client.post(f'/products/admin/{product.id}/edit', data={
            'name': 'Updated Product Name',
            'description': product.description,
            'price': product.price,
            'stock_quantity': product.stock_quantity,
            'category': product.category,
            'sku': product.sku,
            'is_featured': 'y'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Product updated successfully' in response.data

        # Verify product was updated
        updated_product = Product.query.get(product.id)
        assert updated_product.name == 'Updated Product Name'
        assert updated_product.is_featured is True

    def test_admin_toggle_product_active(self, admin_client, init_database):
        """Test toggling product active status"""
        product = Product.query.first()
        response = admin_client.post(f'/products/admin/{product.id}/toggle_active')
        assert response.status_code == 200
        assert response.json['success'] is True

        # Verify product status was toggled
        updated_product = Product.query.get(product.id)
        assert updated_product.is_active is not product.is_active

    def test_admin_toggle_product_featured(self, admin_client, init_database):
        """Test toggling product featured status"""
        product = Product.query.first()
        response = admin_client.post(f'/products/admin/{product.id}/toggle_featured')
        assert response.status_code == 200
        assert response.json['success'] is True

        # Verify product featured status was toggled
        updated_product = Product.query.get(product.id)
        assert updated_product.is_featured is not product.is_featured

    def test_admin_delete_product_route(self, admin_client, init_database):
        """Test admin delete product route"""
        product = Product.query.first()
        response = admin_client.post(f'/products/admin/{product.id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'Product deleted successfully' in response.data

        # Verify product was deleted
        deleted_product = Product.query.get(product.id)
        assert deleted_product is None

    def test_admin_delete_product_with_orders(self, admin_client, init_database):
        """Test admin delete product route when product is in orders"""
        # Create a product that's referenced in an order
        product = Product(
            name='Product in Order',
            description='Product that is in an order',
            price=39.99,
            stock_quantity=10,
            category='Test'
        )
        init_database.session.add(product)
        init_database.session.commit()

        # Create an order with this product
        user = User.query.filter_by(email='test@example.com').first()
        order = Order(
            user_id=user.id,
            shipping_address='123 Test St',
            total_amount=39.99,
            shipping_amount=5.00,
            tax_amount=3.20
        )
        init_database.session.add(order)

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            unit_price=39.99
        )
        init_database.session.add(order_item)
        init_database.session.commit()

        # Try to delete the product
        response = admin_client.post(f'/products/admin/{product.id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'Cannot delete product as it is referenced in orders' in response.data

        # Verify product still exists
        existing_product = Product.query.get(product.id)
        assert existing_product is not None

    def test_product_search(self, test_client, init_database):
        """Test product search functionality"""
        response = test_client.get('/products/?q=Test')
        assert response.status_code == 200
        assert b'Test Product' in response.data

    def test_product_filter_by_category(self, test_client, init_database):
        """Test product filtering by category"""
        product = Product.query.first()
        response = test_client.get(f'/products/?category={product.category}')
        assert response.status_code == 200
        assert product.category.encode() in response.data

    def test_product_sorting(self, test_client, init_database):
        """Test product sorting functionality"""
        # Test price ascending
        response = test_client.get('/products/?sort_by=price_asc')
        assert response.status_code == 200

        # Test price descending
        response = test_client.get('/products/?sort_by=price_desc')
        assert response.status_code == 200

        # Test newest
        response = test_client.get('/products/?sort_by=newest')
        assert response.status_code == 200

    def test_price_range_filter(self, test_client, init_database):
        """Test product filtering by price range"""
        response = test_client.get('/products/?min_price=10&max_price=30')
        assert response.status_code == 200

        # Verify products are within price range
        products = Product.query.filter(
            Product.price >= 10,
            Product.price <= 30
        ).all()
        for product in products:
            assert product.name.encode() in response.data