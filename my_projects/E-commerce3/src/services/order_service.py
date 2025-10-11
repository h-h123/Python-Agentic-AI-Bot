from src.extensions import db
from src.models.order import Order, OrderItem, OrderStatus
from src.models.cart import Cart, CartItem
from src.models.product import Product
from src.models.user import User
from datetime import datetime
import secrets
import string

class OrderService:
    @staticmethod
    def generate_order_number():
        """Generate a unique order number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        return f"ORD-{timestamp}-{random_part}"

    @staticmethod
    def create_order(user_id, shipping_address, payment_method, billing_address=None,
                     shipping_method='standard', notes=None):
        """Create a new order from the user's cart"""
        cart = Cart.query.filter_by(user_id=user_id, is_active=True).first()
        if not cart or not cart.items:
            return None, "Cart is empty"

        try:
            order_number = OrderService.generate_order_number()
            order = Order(
                user_id=user_id,
                order_number=order_number,
                shipping_address=shipping_address,
                payment_method=payment_method,
                billing_address=billing_address or shipping_address,
                shipping_method=shipping_method,
                notes=notes,
                tax_amount=0.00,
                shipping_cost=10.00 if shipping_method == 'express' else 5.00,
                total_amount=0.00
            )
            order.save()

            # Add order items and reduce stock
            for item in cart.items:
                product = item.product
                if not product.reduce_stock(item.quantity):
                    order.cancel()
                    return None, f"Not enough stock for {product.name}"

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.discounted_price
                )
                order_item.save()

            # Calculate totals
            order.calculate_totals()

            # Clear cart
            cart.clear()

            return order, None

        except Exception as e:
            db.session.rollback()
            return None, f"Error creating order: {str(e)}"

    @staticmethod
    def get_order_by_id(order_id, user_id=None):
        """Get an order by ID, optionally checking if it belongs to a user"""
        order = Order.get_by_id(order_id)

        if user_id and order.user_id != user_id:
            return None

        return order

    @staticmethod
    def get_orders_by_user(user_id, page=1, per_page=10):
        """Get paginated orders for a specific user"""
        return Order.query.filter_by(user_id=user_id)\
                         .order_by(Order.order_date.desc())\
                         .paginate(page=page, per_page=per_page)

    @staticmethod
    def get_all_orders(page=1, per_page=10, status=None):
        """Get paginated orders with optional status filter"""
        query = Order.query.order_by(Order.order_date.desc())

        if status:
            query = query.filter(Order.status == status)

        return query.paginate(page=page, per_page=per_page)

    @staticmethod
    def update_order_status(order_id, new_status, user_id=None, is_admin=False):
        """Update the status of an order"""
        order = Order.get_by_id(order_id)

        if not order:
            return False, "Order not found"

        if user_id and order.user_id != user_id and not is_admin:
            return False, "You don't have permission to update this order"

        try:
            order.update_status(new_status)
            return True, None
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating order status: {str(e)}"

    @staticmethod
    def cancel_order(order_id, user_id):
        """Cancel an order if it's cancellable"""
        order = Order.get_by_id(order_id)

        if not order:
            return False, "Order not found"

        if order.user_id != user_id:
            return False, "You don't have permission to cancel this order"

        if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            return False, "This order cannot be cancelled at this stage"

        try:
            order.cancel()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Error cancelling order: {str(e)}"

    @staticmethod
    def get_order_summary(order_id, user_id=None):
        """Get a summary of an order"""
        order = OrderService.get_order_by_id(order_id, user_id)
        if not order:
            return None

        return {
            'order_number': order.order_number,
            'order_date': order.order_date.isoformat(),
            'status': order.status.value,
            'total_amount': float(order.total_amount),
            'items_count': len(order.items),
            'items': [item.to_dict() for item in order.items]
        }

    @staticmethod
    def process_payment(order_id, payment_details):
        """Process payment for an order (mock implementation)"""
        order = Order.get_by_id(order_id)
        if not order:
            return False, "Order not found"

        if order.payment_status != 'Pending':
            return False, "Payment already processed"

        try:
            # In a real implementation, this would integrate with a payment gateway
            order.payment_status = 'Completed'
            order.save()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Error processing payment: {str(e)}"

    @staticmethod
    def update_shipping_info(order_id, tracking_number, shipping_method, user_id=None, is_admin=False):
        """Update shipping information for an order"""
        order = Order.get_by_id(order_id)

        if not order:
            return False, "Order not found"

        if user_id and order.user_id != user_id and not is_admin:
            return False, "You don't have permission to update this order"

        try:
            order.tracking_number = tracking_number
            order.shipping_method = shipping_method
            order.save()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating shipping info: {str(e)}"