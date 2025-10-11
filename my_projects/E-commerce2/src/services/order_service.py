from src import db
from src.models.order import Order, OrderItem, OrderStatus
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.models.user import User
from flask import current_app
import uuid
from datetime import datetime

class OrderService:
    @staticmethod
    def generate_order_number(user_id):
        """Generate a unique order number."""
        return f"ORD-{uuid.uuid4().hex[:8].upper()}-{datetime.now().strftime('%y%m%d')}-{user_id}"

    @staticmethod
    def create_order(user_id, shipping_data, cart_id=None):
        """
        Create a new order from cart or directly with items.
        Returns (order, error_message)
        """
        cart = None
        if cart_id:
            cart = Cart.query.get(cart_id)
            if not cart or cart.user_id != user_id:
                return None, "Invalid cart"

        if cart and not cart.items:
            return None, "Cart is empty"

        order_number = OrderService.generate_order_number(user_id)

        try:
            order = Order(
                user_id=user_id,
                order_number=order_number,
                shipping_address=shipping_data['shipping_address'],
                billing_address=shipping_data.get('billing_address', shipping_data['shipping_address']),
                payment_method=shipping_data['payment_method'],
                notes=shipping_data.get('notes', ''),
                status=OrderStatus.PENDING,
                shipping_method=shipping_data.get('shipping_method', 'standard'),
                tax_amount=shipping_data.get('tax_amount', 0),
                shipping_cost=shipping_data.get('shipping_cost', 0),
                discount_amount=shipping_data.get('discount_amount', 0)
            )
            order.save()

            if cart:
                for item in cart.items:
                    product = Product.query.get(item.product_id)
                    if not product or not product.decrease_stock(item.quantity):
                        db.session.rollback()
                        return None, f"Not enough stock for {product.name if product else 'product'}"

                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        unit_price=item.unit_price
                    )
                    order_item.save()

                order.calculate_total()
                cart.clear()

            return order, None

        except Exception as e:
            current_app.logger.error(f"Error creating order: {str(e)}")
            db.session.rollback()
            return None, "Failed to create order"

    @staticmethod
    def get_order_by_number(order_number, user_id=None):
        """Get an order by its order number, optionally filtered by user."""
        query = Order.query.filter_by(order_number=order_number)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()

    @staticmethod
    def get_user_orders(user_id, status=None, limit=None):
        """Get all orders for a user, optionally filtered by status."""
        query = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc())

        if status:
            if isinstance(status, list):
                query = query.filter(Order.status.in_(status))
            else:
                query = query.filter_by(status=status)

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def update_order_status(order_number, new_status, user_id=None):
        """Update the status of an order."""
        order = OrderService.get_order_by_number(order_number, user_id)
        if not order:
            return False, "Order not found"

        try:
            order.update_status(new_status)
            return True, None
        except Exception as e:
            current_app.logger.error(f"Error updating order status: {str(e)}")
            db.session.rollback()
            return False, "Failed to update order status"

    @staticmethod
    def cancel_order(order_number, user_id):
        """Cancel an order and restore product stock."""
        order = OrderService.get_order_by_number(order_number, user_id)
        if not order:
            return False, "Order not found"

        if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            return False, "Order cannot be cancelled at this stage"

        try:
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product:
                    product.increase_stock(item.quantity)

            order.cancel()
            return True, None
        except Exception as e:
            current_app.logger.error(f"Error cancelling order: {str(e)}")
            db.session.rollback()
            return False, "Failed to cancel order"

    @staticmethod
    def process_payment(order_number, payment_details):
        """Simulate payment processing for an order."""
        order = OrderService.get_order_by_number(order_number)
        if not order:
            return False, "Order not found"

        if order.status != OrderStatus.PENDING:
            return False, "Order is not in pending state"

        try:
            # In a real implementation, this would integrate with a payment gateway
            order.update_status(OrderStatus.PROCESSING)
            return True, None
        except Exception as e:
            current_app.logger.error(f"Error processing payment: {str(e)}")
            db.session.rollback()
            return False, "Payment processing failed"

    @staticmethod
    def ship_order(order_number, tracking_number=None):
        """Mark an order as shipped."""
        order = OrderService.get_order_by_number(order_number)
        if not order:
            return False, "Order not found"

        if order.status != OrderStatus.PROCESSING:
            return False, "Order must be in processing state to ship"

        try:
            order.mark_as_shipped(tracking_number)
            return True, None
        except Exception as e:
            current_app.logger.error(f"Error shipping order: {str(e)}")
            db.session.rollback()
            return False, "Failed to ship order"

    @staticmethod
    def get_order_summary(order_number, user_id=None):
        """Get a summary of an order."""
        order = OrderService.get_order_by_number(order_number, user_id)
        if not order:
            return None

        return {
            'order_number': order.order_number,
            'status': order.status.value,
            'created_at': order.created_at,
            'total_amount': float(order.total_amount),
            'item_count': sum(item.quantity for item in order.items),
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else "Deleted Product",
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'subtotal': item.get_subtotal()
            } for item in order.items]
        }

    @staticmethod
    def calculate_order_totals(order_id):
        """Recalculate all totals for an order."""
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        try:
            order.calculate_total()
            return True, None
        except Exception as e:
            current_app.logger.error(f"Error calculating order totals: {str(e)}")
            db.session.rollback()
            return False, "Failed to calculate order totals"

    @staticmethod
    def get_orders_by_status(status, limit=None):
        """Get orders filtered by status."""
        if isinstance(status, str):
            status = OrderStatus(status)

        query = Order.query.filter_by(status=status).order_by(Order.created_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_recent_orders(limit=10):
        """Get the most recent orders."""
        return Order.query.order_by(Order.created_at.desc()).limit(limit).all()