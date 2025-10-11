from src import db
from src.models.product import Product, Category
from flask import current_app
from sqlalchemy import or_, and_

class ProductService:
    @staticmethod
    def get_all_products(active_only=True, page=1, per_page=10):
        """Get all products with optional pagination and active filter."""
        query = Product.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)

    @staticmethod
    def get_product_by_id(product_id, active_only=True):
        """Get a product by its ID."""
        query = Product.query.filter_by(id=product_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.first_or_404()

    @staticmethod
    def get_product_by_slug(slug, active_only=True):
        """Get a product by its slug."""
        query = Product.query.filter_by(slug=slug)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.first_or_404()

    @staticmethod
    def search_products(query, active_only=True, page=1, per_page=10):
        """Search products by name or description."""
        base_query = Product.query
        if active_only:
            base_query = base_query.filter_by(is_active=True)

        search_query = base_query.filter(
            or_(
                Product.name.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%')
            )
        )
        return search_query.paginate(page=page, per_page=per_page)

    @staticmethod
    def get_products_by_category(category_slug, active_only=True, page=1, per_page=10):
        """Get products by category slug."""
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = Product.query.filter_by(category_id=category.id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.paginate(page=page, per_page=per_page)

    @staticmethod
    def get_featured_products(limit=8, active_only=True):
        """Get featured products."""
        query = Product.query.filter_by(is_featured=True)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Product.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_products_in_price_range(min_price, max_price, active_only=True, page=1, per_page=10):
        """Get products within a specific price range."""
        query = Product.query.filter(and_(Product.price >= min_price, Product.price <= max_price))
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Product.price.asc()).paginate(page=page, per_page=per_page)

    @staticmethod
    def get_related_products(product_id, category_id=None, limit=4):
        """Get related products (same category or similar)."""
        product = Product.query.get(product_id)
        if not product:
            return []

        query = Product.query.filter(
            Product.id != product_id,
            Product.is_active == True
        )

        if category_id:
            query = query.filter_by(category_id=category_id)
        else:
            query = query.filter_by(category_id=product.category_id)

        return query.order_by(Product.created_at.desc()).limit(limit).all()

    @staticmethod
    def check_product_stock(product_id, quantity=1):
        """Check if a product has sufficient stock."""
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return False, "Product not found or inactive"

        if not product.is_in_stock():
            return False, "Product is out of stock"

        if product.stock_quantity < quantity:
            return False, f"Only {product.stock_quantity} items available"

        return True, "Stock available"

    @staticmethod
    def update_product_stock(product_id, quantity_change):
        """Update product stock quantity."""
        product = Product.query.get(product_id)
        if not product:
            return False, "Product not found"

        try:
            if quantity_change > 0:
                product.increase_stock(quantity_change)
            else:
                if not product.decrease_stock(abs(quantity_change)):
                    return False, "Insufficient stock"

            return True, "Stock updated successfully"
        except Exception as e:
            current_app.logger.error(f"Error updating product stock: {str(e)}")
            db.session.rollback()
            return False, "Failed to update stock"

    @staticmethod
    def get_low_stock_products(threshold=5):
        """Get products with stock below a certain threshold."""
        return Product.query.filter(
            Product.is_active == True,
            Product.stock_quantity <= threshold
        ).order_by(Product.stock_quantity.asc()).all()

    @staticmethod
    def get_product_categories(active_only=True):
        """Get all product categories."""
        query = Category.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Category.name.asc()).all()

    @staticmethod
    def get_category_by_slug(slug, active_only=True):
        """Get a category by its slug."""
        query = Category.query.filter_by(slug=slug)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.first_or_404()

    @staticmethod
    def create_product(product_data):
        """Create a new product."""
        try:
            category = Category.query.get(product_data['category_id'])
            if not category:
                return None, "Category not found"

            product = Product(
                name=product_data['name'],
                description=product_data.get('description', ''),
                price=product_data['price'],
                stock_quantity=product_data.get('stock_quantity', 0),
                sku=product_data['sku'],
                slug=product_data['slug'],
                category_id=product_data['category_id'],
                image_url=product_data.get('image_url', ''),
                is_active=product_data.get('is_active', True)
            )

            product.save()
            return product, None
        except Exception as e:
            current_app.logger.error(f"Error creating product: {str(e)}")
            db.session.rollback()
            return None, "Failed to create product"

    @staticmethod
    def update_product(product_id, update_data):
        """Update an existing product."""
        product = Product.query.get(product_id)
        if not product:
            return None, "Product not found"

        try:
            for key, value in update_data.items():
                if hasattr(product, key) and key != 'id':
                    setattr(product, key, value)

            product.save()
            return product, None
        except Exception as e:
            current_app.logger.error(f"Error updating product: {str(e)}")
            db.session.rollback()
            return None, "Failed to update product"

    @staticmethod
    def delete_product(product_id):
        """Delete a product."""
        product = Product.query.get(product_id)
        if not product:
            return False, "Product not found"

        try:
            product.delete()
            return True, "Product deleted successfully"
        except Exception as e:
            current_app.logger.error(f"Error deleting product: {str(e)}")
            db.session.rollback()
            return False, "Failed to delete product"

    @staticmethod
    def create_category(category_data):
        """Create a new product category."""
        try:
            category = Category(
                name=category_data['name'],
                description=category_data.get('description', ''),
                slug=category_data['slug'],
                is_active=category_data.get('is_active', True)
            )

            category.save()
            return category, None
        except Exception as e:
            current_app.logger.error(f"Error creating category: {str(e)}")
            db.session.rollback()
            return None, "Failed to create category"

    @staticmethod
    def update_category(category_id, update_data):
        """Update an existing category."""
        category = Category.query.get(category_id)
        if not category:
            return None, "Category not found"

        try:
            for key, value in update_data.items():
                if hasattr(category, key) and key != 'id':
                    setattr(category, key, value)

            category.save()
            return category, None
        except Exception as e:
            current_app.logger.error(f"Error updating category: {str(e)}")
            db.session.rollback()
            return None, "Failed to update category"

    @staticmethod
    def delete_category(category_id):
        """Delete a category."""
        category = Category.query.get(category_id)
        if not category:
            return False, "Category not found"

        try:
            # Check if category has products
            if Product.query.filter_by(category_id=category_id).count() > 0:
                return False, "Cannot delete category with products"

            category.delete()
            return True, "Category deleted successfully"
        except Exception as e:
            current_app.logger.error(f"Error deleting category: {str(e)}")
            db.session.rollback()
            return False, "Failed to delete category"