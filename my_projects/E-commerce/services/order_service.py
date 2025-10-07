from flask import current_app
from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.cart import Cart, CartItem
from ..models.product import Product
from ..models.user import Address
from .. import db
from datetime import datetime
from decimal import Decimal

class OrderService:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def create_order(self, user_id, shipping_address_id, billing_address_id=None,
                    payment_method='credit_card', notes=None):
        """Create a new order from the user's cart"""
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            return None, "Cart is empty"

        # Validate cart items
        for item in cart.items:
            product = item.product
            if not product.is_active or not product.is_in_stock():
                return None, f"Product {product.name} is no longer available"
            if item.quantity > product.stock:
                return None, f"Only {product.stock} items of {product.name} available in stock"

        # Calculate order total
        subtotal = Decimal('0.00')
        for item in cart.items:
            subtotal += item.product.get_current_price() * item.quantity

        # Create order number
        order_number = self._generate_order_number(user_id)

        # Create order
        order = Order(
            user_id=user_id,
            order_number=order_number,
            status=OrderStatus.PENDING,
            total_amount=subtotal,
            shipping_address_id=shipping_address_id,
            billing_address_id=billing_address_id or shipping_address_id,
            payment_method=payment_method,
            payment_status=PaymentStatus.PENDING,
            notes=notes
        )
        db.session.add(order)

        # Create order items and update product stock
        for item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name,
                product_sku=item.product.sku,
                quantity=item.quantity,
                unit_price=item.product.get_current_price()
            )
            db.session.add(order_item)

            # Update product stock
            item.product.stock -= item.quantity

        db.session.commit()

        # Clear the cart
        cart.clear()

        return order, None

    def get_order_by_id(self, order_id, user_id=None):
        """Get an order by ID, optionally checking user ownership"""
        order = Order.query.get(order_id)
        if not order:
            return None, "Order not found"

        if user_id and order.user_id != user_id:
            return None, "Unauthorized access to order"

        return order, None

    def get_orders_by_user(self, user_id, page=1, per_page=10):
        """Get paginated orders for a user"""
        orders = Order.query.filter_by(user_id=user_id)\
            .order_by(db.desc(Order.created_at))\
            .paginate(page=page, per_page=per_page)
        return orders, None

    def update_order_status(self, order_id, new_status, user_id=None, is_admin=False):
        """Update the status of an order"""
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        if user_id and order.user_id != user_id and not is_admin:
            return False, "Unauthorized to update order status"

        try:
            order.update_status(new_status)
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def update_payment_status(self, order_id, new_status, user_id=None, is_admin=False):
        """Update the payment status of an order"""
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        if user_id and order.user_id != user_id and not is_admin:
            return False, "Unauthorized to update payment status"

        try:
            order.update_payment_status(new_status)
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def cancel_order(self, order_id, user_id):
        """Cancel an order and restore product stock"""
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        if order.user_id != user_id:
            return False, "Unauthorized to cancel order"

        if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            return False, "Order cannot be cancelled at this stage"

        try:
            # Restore product stock
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock += item.quantity

            order.mark_as_cancelled()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def process_payment(self, order_id, payment_reference, payment_status):
        """Process payment for an order"""
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        try:
            order.payment_reference = payment_reference
            order.update_payment_status(payment_status)

            if payment_status == PaymentStatus.COMPLETED:
                order.update_status(OrderStatus.PROCESSING)

            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def calculate_shipping_cost(self, order_id):
        """Calculate shipping cost for an order (placeholder implementation)"""
        order = Order.query.get(order_id)
        if not order:
            return None, "Order not found"

        # Basic shipping calculation - would be more complex in a real application
        shipping_cost = Decimal('5.00')  # Flat rate
        if order.total_amount > Decimal('50.00'):
            shipping_cost = Decimal('0.00')  # Free shipping over $50

        return shipping_cost, None

    def calculate_tax(self, order_id):
        """Calculate tax for an order (placeholder implementation)"""
        order = Order.query.get(order_id)
        if not order:
            return None, "Order not found"

        # Basic tax calculation - would vary by location in a real application
        tax_rate = Decimal('0.08')  # 8% tax
        tax_amount = order.total_amount * tax_rate

        return tax_amount, None

    def update_order_totals(self, order_id):
        """Recalculate and update order totals"""
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        try:
            subtotal = sum(item.quantity * item.unit_price for item in order.items)
            shipping_cost, _ = self.calculate_shipping_cost(order_id)
            tax_amount, _ = self.calculate_tax(order_id)

            order.total_amount = subtotal + shipping_cost + tax_amount
            order.shipping_amount = shipping_cost
            order.tax_amount = tax_amount

            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def _generate_order_number(self, user_id):
        """Generate a unique order number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"ORD-{timestamp}-{user_id}"

    def get_order_items(self, order_id):
        """Get all items for an order"""
        order = Order.query.get(order_id)
        if not order:
            return None, "Order not found"

        return order.items, None

    def get_order_summary(self, order_id):
        """Get a summary of an order"""
        order = Order.query.get(order_id)
        if not order:
            return None, "Order not found"

        summary = {
            'order_number': order.order_number,
            'status': order.status.value,
            'payment_status': order.payment_status.value,
            'total_amount': float(order.total_amount),
            'item_count': order.get_order_items_count(),
            'created_at': order.created_at.isoformat()
        }

        return summary, None

    def mark_order_as_shipped(self, order_id, tracking_number=None, is_admin=False):
        """Mark an order as shipped"""
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        if not is_admin:
            return False, "Unauthorized to update order status"

        if order.status != OrderStatus.PROCESSING:
            return False, "Order cannot be shipped at this stage"

        try:
            order.status = OrderStatus.SHIPPED
            order.tracking_number = tracking_number
            order.updated_at = datetime.utcnow()
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def mark_order_as_delivered(self, order_id, is_admin=False):
        """Mark an order as delivered"""
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        if not is_admin:
            return False, "Unauthorized to update order status"

        if order.status != OrderStatus.SHIPPED:
            return False, "Order cannot be marked as delivered at this stage"

        try:
            order.mark_as_completed()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def get_order_history(self, user_id, status=None, limit=10):
        """Get recent order history for a user"""
        query = Order.query.filter_by(user_id=user_id).order_by(db.desc(Order.created_at))

        if status:
            query = query.filter_by(status=status)

        orders = query.limit(limit).all()
        return orders, None