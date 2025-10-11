from src.extensions import db
from src.models.product import Product, ProductCategory
from src.models.base import BaseModel
from werkzeug.utils import secure_filename
from flask import current_app
import os

class ProductService:
    @staticmethod
    def get_all_products(page=1, per_page=10, category_id=None, active_only=True):
        """Get paginated list of products with optional category filter"""
        query = Product.query

        if active_only:
            query = query.filter_by(is_active=True)

        if category_id:
            query = query.filter_by(category_id=category_id)

        return query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)

    @staticmethod
    def get_product_by_id(product_id):
        """Get a product by ID"""
        return Product.get_by_id(product_id)

    @staticmethod
    def create_product(name, description, price, stock, category_id=None,
                      sku=None, discount=0.00, image=None):
        """Create a new product"""
        try:
            filename = None
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

            product = Product(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category_id=category_id,
                sku=sku,
                discount=discount,
                image=filename
            )
            product.save()
            return product, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def update_product(product_id, **kwargs):
        """Update an existing product"""
        product = Product.get_by_id(product_id)
        if not product:
            return False, "Product not found"

        try:
            if 'image' in kwargs and kwargs['image']:
                image = kwargs.pop('image')
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

                if product.image and product.image != 'default-product.jpg':
                    old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                product.image = filename

            product.update(**kwargs)
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def delete_product(product_id):
        """Delete a product"""
        product = Product.get_by_id(product_id)
        if not product:
            return False, "Product not found"

        try:
            if product.image and product.image != 'default-product.jpg':
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image)
                if os.path.exists(image_path):
                    os.remove(image_path)

            product.delete()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def search_products(query, page=1, per_page=10):
        """Search products by name or description"""
        return Product.query.filter(
            Product.is_active == True,
            Product.name.ilike(f'%{query}%')
        ).paginate(page=page, per_page=per_page)

    @staticmethod
    def get_featured_products(limit=8):
        """Get featured products (most recent active products)"""
        return Product.query.filter_by(is_active=True)\
            .order_by(Product.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def update_product_stock(product_id, quantity_change):
        """Update product stock by a specific quantity"""
        product = Product.get_by_id(product_id)
        if not product:
            return False, "Product not found"

        try:
            new_stock = product.stock + quantity_change
            if new_stock < 0:
                return False, "Stock cannot be negative"

            product.stock = new_stock
            product.save()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_products_by_category(category_id, page=1, per_page=10):
        """Get products by category ID"""
        return Product.query.filter_by(category_id=category_id, is_active=True)\
            .paginate(page=page, per_page=per_page)

    @staticmethod
    def get_all_categories(parent_id=None):
        """Get all product categories with optional parent filter"""
        query = ProductCategory.query.filter_by(is_active=True)
        if parent_id is not None:
            query = query.filter_by(parent_id=parent_id)
        return query.all()

    @staticmethod
    def get_category_by_id(category_id):
        """Get a category by ID"""
        return ProductCategory.get_by_id(category_id)

    @staticmethod
    def create_category(name, description=None, parent_id=None):
        """Create a new product category"""
        try:
            category = ProductCategory(
                name=name,
                description=description,
                parent_id=parent_id
            )
            category.save()
            return category, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def update_category(category_id, **kwargs):
        """Update an existing category"""
        category = ProductCategory.get_by_id(category_id)
        if not category:
            return False, "Category not found"

        try:
            category.update(**kwargs)
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def delete_category(category_id):
        """Delete a category"""
        category = ProductCategory.get_by_id(category_id)
        if not category:
            return False, "Category not found"

        try:
            category.delete()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_category_hierarchy():
        """Get all categories organized in a hierarchy"""
        categories = ProductCategory.query.filter_by(is_active=True).all()
        hierarchy = {}

        for category in categories:
            if category.parent_id:
                if category.parent_id not in hierarchy:
                    hierarchy[category.parent_id] = []
                hierarchy[category.parent_id].append(category)
            else:
                if 'root' not in hierarchy:
                    hierarchy['root'] = []
                hierarchy['root'].append(category)

        return hierarchy