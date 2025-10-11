from src import db
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.models.user import User
from flask import current_app

class CartService:
    @staticmethod
    def get_active_cart(user_id):
        """Get the active cart for a user or create a new one if none exists."""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart:
            cart = Cart(user_id=user_id)
            cart.save()
        return cart

    @staticmethod
    def add_item_to_cart(user_id, product_id, quantity=1):
        """Add a product to the user's cart."""
        cart = CartService.get_active_cart(user_id)
        product = Product.query.get(product_id)

        if not product:
            return None, "Product not found"

        if not product.is_in_stock():
            return None, "Product is out of stock"

        if quantity > product.stock_quantity:
            quantity = product.stock_quantity
            current_app.logger.warning(f"Adjusted quantity for product {product_id} to available stock")

        try:
            cart_item = cart.add_item(product, quantity)
            return cart_item, None
        except Exception as e:
            current_app.logger.error(f"Error adding item to cart: {str(e)}")
            db.session.rollback()
            return None, "Failed to add item to cart"

    @staticmethod
    def update_cart_item(user_id, item_id, quantity):
        """Update the quantity of a cart item."""
        item = CartItem.query.get(item_id)
        if not item:
            return None, "Cart item not found"

        cart = Cart.query.get(item.cart_id)
        if cart.user_id != user_id:
            return None, "Unauthorized access to cart item"

        product = Product.query.get(item.product_id)
        if not product:
            return None, "Product not found"

        if quantity <= 0:
            cart.remove_item(item.product_id)
            return None, "Item removed from cart"

        if quantity > product.stock_quantity:
            return None, f"Only {product.stock_quantity} items available in stock"

        try:
            updated_item = cart.update_item_quantity(item.product_id, quantity)
            return updated_item, None
        except Exception as e:
            current_app.logger.error(f"Error updating cart item: {str(e)}")
            db.session.rollback()
            return None, "Failed to update cart item"

    @staticmethod
    def remove_cart_item(user_id, item_id):
        """Remove an item from the cart."""
        item = CartItem.query.get(item_id)
        if not item:
            return None, "Cart item not found"

        cart = Cart.query.get(item.cart_id)
        if cart.user_id != user_id:
            return None, "Unauthorized access to cart item"

        try:
            removed_item = cart.remove_item(item.product_id)
            return removed_item, None
        except Exception as e:
            current_app.logger.error(f"Error removing cart item: {str(e)}")
            db.session.rollback()
            return None, "Failed to remove cart item"

    @staticmethod
    def clear_cart(user_id):
        """Clear all items from the cart."""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart:
            return None, "No active cart found"

        try:
            cleared_cart = cart.clear()
            return cleared_cart, None
        except Exception as e:
            current_app.logger.error(f"Error clearing cart: {str(e)}")
            db.session.rollback()
            return None, "Failed to clear cart"

    @staticmethod
    def get_cart_summary(user_id):
        """Get a summary of the user's cart."""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart:
            return {
                'item_count': 0,
                'total_price': 0.0,
                'items': []
            }

        # Update prices in case they changed
        for item in cart.items:
            item.update_price()

        return {
            'item_count': cart.get_total_items(),
            'total_price': cart.get_total_price(),
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'subtotal': item.get_subtotal(),
                'image_url': item.product.image_url
            } for item in cart.items]
        }

    @staticmethod
    def merge_carts(source_user_id, target_user_id):
        """Merge carts when a guest user logs in or when combining accounts."""
        source_cart = Cart.query.filter_by(user_id=source_user_id, is_active=True).first()
        target_cart = CartService.get_active_cart(target_user_id)

        if not source_cart or not source_cart.items:
            return target_cart, None

        try:
            for item in source_cart.items[:]:  # Create a copy of the list to iterate
                product = Product.query.get(item.product_id)
                if product and product.is_in_stock():
                    target_cart.add_item(product, item.quantity)
                item.delete()

            source_cart.is_active = False
            source_cart.save()
            return target_cart, None
        except Exception as e:
            current_app.logger.error(f"Error merging carts: {str(e)}")
            db.session.rollback()
            return None, "Failed to merge carts"

    @staticmethod
    def validate_cart_stock(user_id):
        """Check if all items in the cart have sufficient stock."""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart or not cart.items:
            return True, None

        insufficient_stock = []
        for item in cart.items:
            product = Product.query.get(item.product_id)
            if not product or not product.is_in_stock() or product.stock_quantity < item.quantity:
                insufficient_stock.append({
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else "Unknown Product",
                    'available': product.stock_quantity if product else 0,
                    'requested': item.quantity
                })

        if insufficient_stock:
            return False, insufficient_stock
        return True, None