from flask import current_app
from ..models.product import Product, Category, ProductImage, Review
from ..models.user import User
from .. import db
from sqlalchemy import or_, func, desc
from datetime import datetime, timedelta
from decimal import Decimal
import math

class ProductService:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def get_product_by_id(self, product_id):
        """Get a product by its ID"""
        product = Product.query.get(product_id)
        if not product:
            return None, "Product not found"
        return product, None

    def get_active_product_by_id(self, product_id):
        """Get an active product by its ID"""
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            return None, "Product not found or inactive"
        return product, None

    def get_products_by_ids(self, product_ids):
        """Get multiple products by their IDs"""
        products = Product.query.filter(Product.id.in_(product_ids), Product.is_active=True).all()
        return products, None

    def search_products(self, query=None, category_id=None, min_price=None, max_price=None,
                        in_stock=None, page=1, per_page=12, sort_by='name', sort_order='asc'):
        """Search for products with various filters"""
        base_query = Product.query.filter_by(is_active=True)

        if query:
            search_term = f"%{query}%"
            base_query = base_query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )

        if category_id:
            # Get all subcategory IDs if category_id is provided
            category = Category.query.get(category_id)
            if category:
                subcategory_ids = [cat.id for cat in category.subcategories] + [category_id]
                base_query = base_query.filter(Product.category_id.in_(subcategory_ids))
            else:
                return [], None

        if min_price is not None:
            base_query = base_query.filter(Product.price >= min_price)

        if max_price is not None:
            base_query = base_query.filter(Product.price <= max_price)

        if in_stock is not None:
            if in_stock:
                base_query = base_query.filter(Product.stock > 0)
            else:
                base_query = base_query.filter(Product.stock <= 0)

        # Apply sorting
        if sort_by == 'price':
            sort_column = Product.price
        elif sort_by == 'created_at':
            sort_column = Product.created_at
        elif sort_by == 'rating':
            sort_column = self._get_avg_rating_subquery()
        else:  # default to name
            sort_column = Product.name

        if sort_order == 'desc':
            sort_column = sort_column.desc()

        # Paginate results
        products = base_query.order_by(sort_column).paginate(page=page, per_page=per_page)
        return products, None

    def get_featured_products(self, limit=4):
        """Get featured products"""
        products = Product.query.filter_by(is_featured=True, is_active=True).limit(limit).all()
        return products, None

    def get_new_arrivals(self, days=30, limit=8):
        """Get recently added products"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        products = Product.query.filter(
            Product.is_active == True,
            Product.created_at >= cutoff_date
        ).order_by(Product.created_at.desc()).limit(limit).all()
        return products, None

    def get_best_sellers(self, limit=8):
        """Get best selling products (simplified implementation)"""
        products = Product.query.filter_by(is_active=True)\
            .order_by(Product.stock.asc()).limit(limit).all()
        return products, None

    def get_products_by_category(self, category_slug, page=1, per_page=12):
        """Get products by category slug"""
        category = Category.query.filter_by(slug=category_slug, is_active=True).first()
        if not category:
            return None, "Category not found"

        products = Product.query.filter_by(
            category_id=category.id,
            is_active=True
        ).order_by(Product.name).paginate(page=page, per_page=per_page)

        return products, None

    def get_related_products(self, product_id, category_id=None, limit=4):
        """Get related products (same category)"""
        if not category_id:
            product = self.get_product_by_id(product_id)
            if product:
                category_id = product.category_id
            else:
                return [], None

        products = Product.query.filter(
            Product.category_id == category_id,
            Product.id != product_id,
            Product.is_active == True
        ).limit(limit).all()

        return products, None

    def get_product_reviews(self, product_id, approved_only=True, page=1, per_page=5):
        """Get reviews for a product"""
        query = Review.query.filter_by(product_id=product_id)

        if approved_only:
            query = query.filter_by(is_approved=True)

        reviews = query.order_by(desc(Review.created_at))\
            .paginate(page=page, per_page=per_page)

        return reviews, None

    def get_product_rating(self, product_id):
        """Get average rating for a product"""
        product = self.get_product_by_id(product_id)
        if not product:
            return 0, None

        if not product.reviews:
            return 0, None

        avg_rating = db.session.query(func.avg(Review.rating))\
            .filter(Review.product_id == product_id)\
            .scalar()

        return round(float(avg_rating or 0), 1), None

    def add_product_review(self, user_id, product_id, rating, comment):
        """Add a review for a product"""
        user = User.query.get(user_id)
        product = self.get_active_product_by_id(product_id)

        if not user or not product:
            return None, "User or product not found"

        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()

        if existing_review:
            return None, "You have already reviewed this product"

        if rating < 1 or rating > 5:
            return None, "Rating must be between 1 and 5"

        review = Review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment,
            is_approved=True  # In production, you might want to moderate reviews first
        )

        db.session.add(review)
        db.session.commit()

        return review, None

    def update_product_stock(self, product_id, quantity_change):
        """Update product stock level"""
        product = self.get_active_product_by_id(product_id)
        if not product:
            return False, "Product not found"

        new_stock = product.stock + quantity_change
        if new_stock < 0:
            return False, "Insufficient stock"

        product.stock = new_stock
        product.updated_at = datetime.utcnow()
        db.session.commit()

        return True, None

    def check_product_availability(self, product_id, quantity=1):
        """Check if a product is available in the requested quantity"""
        product = self.get_active_product_by_id(product_id)
        if not product:
            return False, "Product not found or inactive"

        if not product.is_in_stock():
            return False, "Product out of stock"

        if quantity > product.stock:
            return False, f"Only {product.stock} items available"

        return True, None

    def get_category_by_slug(self, slug):
        """Get a category by its slug"""
        category = Category.query.filter_by(slug=slug, is_active=True).first()
        if not category:
            return None, "Category not found"
        return category, None

    def get_category_tree(self):
        """Get all categories in a hierarchical tree structure"""
        categories = Category.query.filter_by(is_active=True, parent_id=None)\
            .order_by(Category.display_order).all()

        def build_tree(category):
            children = Category.query.filter_by(parent_id=category.id, is_active=True)\
                .order_by(Category.display_order).all()

            return {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'children': [build_tree(child) for child in children]
            }

        return [build_tree(category) for category in categories], None

    def get_all_categories(self):
        """Get all active categories"""
        categories = Category.query.filter_by(is_active=True)\
            .order_by(Category.name).all()
        return categories, None

    def get_products_on_sale(self, limit=8):
        """Get products that are on sale (have discount_price set)"""
        products = Product.query.filter(
            Product.is_active == True,
            Product.discount_price.isnot(None),
            Product.discount_price < Product.price
        ).limit(limit).all()
        return products, None

    def get_product_price(self, product_id):
        """Get the current price of a product (considering discounts)"""
        product = self.get_active_product_by_id(product_id)
        if not product:
            return None, "Product not found"

        return product.get_current_price(), None

    def _get_avg_rating_subquery(self):
        """Helper method to create a subquery for average rating"""
        subquery = db.session.query(
            Review.product_id,
            func.avg(Review.rating).label('avg_rating')
        ).group_by(Review.product_id).subquery()

        return func.coalesce(subquery.c.avg_rating, 0)

    def get_popular_products(self, limit=8, days=30):
        """Get popular products based on recent sales (simplified)"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # This is a simplified implementation - in a real app you'd track actual sales
        products = Product.query.join(Review)\
            .filter(
                Product.is_active == True,
                Review.created_at >= cutoff_date
            )\
            .group_by(Product.id)\
            .order_by(func.count(Review.id).desc())\
            .limit(limit)\
            .all()

        return products, None

    def get_product_images(self, product_id):
        """Get all images for a product"""
        product = self.get_product_by_id(product_id)
        if not product:
            return [], "Product not found"

        images = ProductImage.query.filter_by(product_id=product_id)\
            .order_by(ProductImage.display_order).all()

        return images, None

    def get_primary_product_image(self, product_id):
        """Get the primary image for a product"""
        image = ProductImage.query.filter_by(
            product_id=product_id,
            is_primary=True
        ).first()

        if not image and product_id:
            # Fallback to first image if no primary is set
            image = ProductImage.query.filter_by(product_id=product_id)\
                .order_by(ProductImage.display_order).first()

        return image, None

    def calculate_discount_percentage(self, product_id):
        """Calculate the discount percentage for a product"""
        product = self.get_active_product_by_id(product_id)
        if not product or not product.discount_price:
            return 0, None

        if product.price <= 0:
            return 0, None

        discount = product.price - product.discount_price
        percentage = (discount / product.price) * 100
        return round(percentage, 0), None

    def get_similar_products(self, product_id, limit=4):
        """Get products similar to the given product (same category, similar price)"""
        product = self.get_active_product_by_id(product_id)
        if not product:
            return [], None

        # Get products in same category with price within 20% of current product
        price_range = product.price * 0.2
        min_price = product.price - price_range
        max_price = product.price + price_range

        similar_products = Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product_id,
            Product.is_active == True,
            Product.price.between(min_price, max_price)
        ).order_by(Product.price).limit(limit).all()

        return similar_products, None

    def get_product_availability_status(self, product):
        """Get a human-readable availability status for a product"""
        if not product.is_active:
            return "Unavailable"

        if product.stock <= 0:
            return "Out of Stock"

        if product.stock < 5:
            return "Low Stock"

        if product.stock < 20:
            return "Limited Stock"

        return "In Stock"