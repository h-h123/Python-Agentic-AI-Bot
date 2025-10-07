from flask import current_app
from ..models.cart import Cart, CartItem
from ..models.product import Product
from .. import db
from decimal import Decimal

class CartService:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def get_or_create_cart(self, user_id):
        """Get or create a cart for the given user"""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        return cart

    def add_item_to_cart(self, user_id, product_id, quantity=1):
        """Add a product to the user's cart"""
        product = Product.query.get(product_id)
        if not product or not product.is_active or not product.is_in_stock():
            return False, "Product not available"

        if quantity <= 0:
            return False, "Quantity must be at least 1"

        if quantity > product.stock:
            return False, f"Only {product.stock} items available in stock"

        cart = self.get_or_create_cart(user_id)
        return cart.add_item(product, quantity), None

    def update_cart_item(self, user_id, product_id, quantity):
        """Update the quantity of a product in the cart"""
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return False, "Product not available"

        if quantity <= 0:
            return self.remove_item_from_cart(user_id, product_id)

        if quantity > product.stock:
            return False, f"Only {product.stock} items available in stock"

        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            return False, "Cart not found"

        cart.update_item_quantity(product, quantity)
        return True, None

    def remove_item_from_cart(self, user_id, product_id):
        """Remove a product from the user's cart"""
        product = Product.query.get(product_id)
        if not product:
            return False, "Product not found"

        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            return False, "Cart not found"

        cart.remove_item(product)
        return True, None

    def clear_cart(self, user_id):
        """Clear all items from the user's cart"""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            cart.clear()
            return True, None
        return False, "Cart not found"

    def get_cart_total(self, user_id):
        """Get the total price of all items in the cart"""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            return Decimal(cart.get_total_price()), None
        return Decimal('0.00'), None

    def get_cart_item_count(self, user_id):
        """Get the total number of items in the cart"""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            return cart.get_total_items(), None
        return 0, None

    def get_cart_items(self, user_id):
        """Get all items in the user's cart"""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            return cart.items, None
        return [], None

    def validate_cart(self, user_id):
        """Validate that all items in the cart are still available"""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            return False, "Cart is empty"

        for item in cart.items:
            product = item.product
            if not product.is_active or not product.is_in_stock():
                return False, f"Product {product.name} is no longer available"
            if item.quantity > product.stock:
                return False, f"Only {product.stock} items of {product.name} available in stock"

        return True, None

    def merge_carts(self, source_user_id, target_user_id):
        """Merge carts from one user to another (useful for guest checkout)"""
        source_cart = Cart.query.filter_by(user_id=source_user_id).first()
        target_cart = self.get_or_create_cart(target_user_id)

        if not source_cart or not source_cart.items:
            return True, None

        for item in source_cart.items:
            product = item.product
            if product.is_active and product.is_in_stock():
                target_cart.add_item(product, item.quantity)

        # Clear the source cart
        source_cart.clear()
        return True, None

    def apply_discount(self, user_id, discount_code):
        """Apply a discount code to the cart (placeholder for future implementation)"""
        # This would be implemented with a proper discount system
        return False, "Discount feature not implemented yet"