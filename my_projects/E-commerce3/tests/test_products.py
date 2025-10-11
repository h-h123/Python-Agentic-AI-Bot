import pytest
from flask import url_for
from src.models.product import Product, ProductCategory
from src.services.product_service import ProductService

class TestProductRoutes:
    def test_product_list_route(self, test_client, init_database):
        # Test GET request to product list
        response = test_client.get('/products/')
        assert response.status_code == 200
        assert b'Test Product' in response.data

    def test_product_detail_route(self, test_client, init_database):
        product = Product.query.first()
        response = test_client.get(f'/products/{product.id}')
        assert response.status_code == 200
        assert product.name.encode() in response.data

    def test_add_product_route_unauthorized(self, test_client, init_database):
        # Test unauthorized access to add product
        response = test_client.get('/products/add')
        assert response.status_code == 302  # Redirect to login

    def test_add_product_route_authorized(self, admin_client, init_database):
        # Test GET request to add product page
        response = admin_client.get('/products/add')
        assert response.status_code == 200
        assert b'Add Product' in response.data

    def test_add_product_form_submission(self, admin_client, init_database):
        category = ProductCategory.query.first()
        response = admin_client.post('/products/add', data={
            'name': 'New Product',
            'description': 'New product description',
            'price': '19.99',
            'stock': '50',
            'category': str(category.id),
            'sku': 'NEW001',
            'discount': '0'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Product added successfully!' in response.data

    def test_edit_product_route(self, admin_client, init_database):
        product = Product.query.first()
        response = admin_client.get(f'/products/{product.id}/edit')
        assert response.status_code == 200
        assert b'Edit Product' in response.data

    def test_delete_product_route(self, admin_client, init_database):
        product = Product.query.first()
        response = admin_client.post(f'/products/{product.id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'Product deleted successfully!' in response.data

    def test_category_list_route(self, test_client, init_database):
        response = test_client.get('/products/categories')
        assert response.status_code == 200
        assert b'Test Category' in response.data

    def test_add_to_cart_route(self, logged_in_client, init_database):
        product = Product.query.first()
        response = logged_in_client.post(f'/products/{product.id}/add_to_cart', data={
            'quantity': '1'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Product added to cart successfully!' in response.data

class TestProductService:
    def test_get_all_products(self, init_database):
        products = ProductService.get_all_products()
        assert products.total == 1
        assert products.items[0].name == 'Test Product'

    def test_get_product_by_id(self, init_database):
        product = Product.query.first()
        fetched_product = ProductService.get_product_by_id(product.id)
        assert fetched_product is not None
        assert fetched_product.name == product.name

    def test_create_product(self, init_database):
        category = ProductCategory.query.first()
        product, error = ProductService.create_product(
            name='Service Product',
            description='Product created via service',
            price=29.99,
            stock=30,
            category_id=category.id,
            sku='SERV001'
        )
        assert product is not None
        assert error is None
        assert product.name == 'Service Product'

    def test_update_product(self, init_database):
        product = Product.query.first()
        success, error = ProductService.update_product(
            product.id,
            name='Updated Product',
            price=24.99
        )
        assert success is True
        assert error is None
        updated_product = Product.query.get(product.id)
        assert updated_product.name == 'Updated Product'
        assert updated_product.price == 24.99

    def test_delete_product(self, init_database):
        product = Product.query.first()
        success, error = ProductService.delete_product(product.id)
        assert success is True
        assert error is None
        assert Product.query.get(product.id) is None

    def test_search_products(self, init_database):
        products = ProductService.search_products('Test')
        assert products.total == 1
        assert products.items[0].name == 'Test Product'

    def test_get_featured_products(self, init_database):
        products = ProductService.get_featured_products()
        assert len(products) == 1
        assert products[0].name == 'Test Product'

    def test_get_products_by_category(self, init_database):
        category = ProductCategory.query.first()
        products = ProductService.get_products_by_category(category.id)
        assert products.total == 1
        assert products.items[0].name == 'Test Product'

    def test_get_all_categories(self, init_database):
        categories = ProductService.get_all_categories()
        assert len(categories) == 1
        assert categories[0].name == 'Test Category'

    def test_create_category(self, init_database):
        category, error = ProductService.create_category(
            name='New Category',
            description='New category description'
        )
        assert category is not None
        assert error is None
        assert category.name == 'New Category'

    def test_update_category(self, init_database):
        category = ProductCategory.query.first()
        success, error = ProductService.update_category(
            category.id,
            name='Updated Category'
        )
        assert success is True
        assert error is None
        updated_category = ProductCategory.query.get(category.id)
        assert updated_category.name == 'Updated Category'

    def test_delete_category(self, init_database):
        category = ProductCategory.query.first()
        success, error = ProductService.delete_category(category.id)
        assert success is True
        assert error is None
        assert ProductCategory.query.get(category.id) is None

class TestProductModel:
    def test_product_creation(self, init_database):
        category = ProductCategory.query.first()
        product = Product(
            name='Model Test Product',
            description='Product for model testing',
            price=39.99,
            stock=25,
            category_id=category.id,
            sku='MODEL001'
        )
        product.save()
        assert product.id is not None
        assert product.name == 'Model Test Product'
        assert product.discounted_price == 39.99

    def test_product_discount(self, init_database):
        category = ProductCategory.query.first()
        product = Product(
            name='Discount Product',
            description='Product with discount',
            price=100.00,
            stock=10,
            category_id=category.id,
            discount=20.00,
            sku='DISC001'
        )
        product.save()
        assert product.discounted_price == 80.00

    def test_product_stock_management(self, init_database):
        category = ProductCategory.query.first()
        product = Product(
            name='Stock Test',
            description='Product for stock testing',
            price=9.99,
            stock=10,
            category_id=category.id,
            sku='STOCK001'
        )
        product.save()

        # Test reduce stock
        assert product.reduce_stock(5) is True
        assert product.stock == 5

        # Test increase stock
        product.increase_stock(3)
        assert product.stock == 8

        # Test reduce stock beyond available
        assert product.reduce_stock(10) is False
        assert product.stock == 8

    def test_product_category_relationship(self, init_database):
        category = ProductCategory.query.first()
        product = Product(
            name='Category Relationship Test',
            description='Product for category relationship testing',
            price=19.99,
            stock=15,
            category_id=category.id,
            sku='CATREL001'
        )
        product.save()

        assert product.category_id == category.id
        assert product in category.products

    def test_product_to_dict(self, init_database):
        product = Product.query.first()
        product_dict = product.to_dict()
        assert product_dict['name'] == product.name
        assert product_dict['price'] == str(product.price)
        assert 'discounted_price' in product_dict
        assert 'in_stock' in product_dict

class TestProductCategoryModel:
    def test_category_creation(self, init_database):
        category = ProductCategory(
            name='New Test Category',
            description='Category for model testing',
            is_active=True
        )
        category.save()
        assert category.id is not None
        assert category.name == 'New Test Category'

    def test_category_hierarchy(self, init_database):
        parent = ProductCategory(
            name='Parent Category',
            description='Parent category',
            is_active=True
        )
        parent.save()

        child = ProductCategory(
            name='Child Category',
            description='Child category',
            parent_id=parent.id,
            is_active=True
        )
        child.save()

        assert child.parent_id == parent.id
        assert child in parent.children

    def test_category_to_dict(self, init_database):
        category = ProductCategory.query.first()
        category_dict = category.to_dict()
        assert category_dict['name'] == category.name
        assert 'parent_id' not in category_dict
        assert category_dict['is_active'] == category.is_active