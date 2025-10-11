from src.extensions import db
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.models.user import User
from flask_login import current_user

class CartService:
    @staticmethod
    def get_active_cart(user_id):
        """Get the active cart for a user, create one if it doesn't exist"""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart:
            cart = Cart(user_id=user_id)
            cart.save()
        return cart

    @staticmethod
    def add_item_to_cart(user_id, product_id, quantity=1):
        """Add an item to the user's cart"""
        product = Product.get_by_id(product_id)
        if not product:
            return False, "Product not found"

        if not product.in_stock:
            return False, "Product is out of stock"

        if quantity > product.stock:
            return False, f"Not enough stock. Only {product.stock} available"

        cart = CartService.get_active_cart(user_id)

        existing_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=product_id
        ).first()

        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.stock:
                return False, f"Cannot add {quantity} more. Only {product.stock - existing_item.quantity} available"
            existing_item.quantity = new_quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(item)

        cart.save()
        return True, "Item added to cart successfully"

    @staticmethod
    def update_cart_item(user_id, item_id, quantity):
        """Update the quantity of an item in the cart"""
        cart_item = CartItem.get_by_id(item_id)
        if not cart_item or cart_item.cart.user_id != user_id:
            return False, "Item not found in your cart"

        product = cart_item.product
        if quantity <= 0:
            return CartService.remove_cart_item(user_id, item_id)

        if quantity > product.stock:
            return False, f"Not enough stock. Only {product.stock} available"

        cart_item.quantity = quantity
        cart_item.save()
        return True, "Cart item updated successfully"

    @staticmethod
    def remove_cart_item(user_id, item_id):
        """Remove an item from the cart"""
        cart_item = CartItem.get_by_id(item_id)
        if not cart_item or cart_item.cart.user_id != user_id:
            return False, "Item not found in your cart"

        cart_item.delete()
        return True, "Item removed from cart successfully"

    @staticmethod
    def clear_cart(user_id):
        """Clear all items from the cart"""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if cart:
            cart.clear()
            return True, "Cart cleared successfully"
        return False, "No active cart found"

    @staticmethod
    def get_cart_summary(user_id):
        """Get a summary of the cart (total items, total price)"""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart:
            return {
                'total_items': 0,
                'total_price': 0.00,
                'items': []
            }

        return {
            'total_items': cart.total_items,
            'total_price': float(cart.total_price),
            'items': [item.to_dict() for item in cart.items]
        }

    @staticmethod
    def merge_carts(source_user_id, target_user_id):
        """Merge carts from one user to another (useful for guest to user conversion)"""
        source_cart = Cart.query.filter_by(user_id=source_user_id, is_active=True).first()
        target_cart = CartService.get_active_cart(target_user_id)

        if not source_cart or not source_cart.items:
            return True, "No items to merge"

        try:
            for item in source_cart.items:
                product = item.product
                if not product.in_stock:
                    continue

                available_quantity = min(item.quantity, product.stock)
                if available_quantity <= 0:
                    continue

                # Check if product already exists in target cart
                existing_item = CartItem.query.filter_by(
                    cart_id=target_cart.id,
                    product_id=product.id
                ).first()

                if existing_item:
                    new_quantity = existing_item.quantity + available_quantity
                    if new_quantity > product.stock:
                        existing_item.quantity = product.stock
                    else:
                        existing_item.quantity = new_quantity
                    existing_item.save()
                else:
                    new_item = CartItem(
                        cart_id=target_cart.id,
                        product_id=product.id,
                        quantity=available_quantity
                    )
                    new_item.save()

            # Clear the source cart
            source_cart.clear()
            return True, "Carts merged successfully"

        except Exception as e:
            db.session.rollback()
            return False, f"Error merging carts: {str(e)}"