from datetime import datetime
from enum import Enum
from . import db

class OrderStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class PaymentStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0.00)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    billing_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_reference = db.Column(db.String(100))
    tracking_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    shipping_address = db.relationship('Address', foreign_keys=[shipping_address_id], backref='shipped_orders')
    billing_address = db.relationship('Address', foreign_keys=[billing_address_id], backref='billed_orders')

    def __repr__(self):
        return f'<Order {self.order_number}>'

    def calculate_total(self):
        subtotal = sum(item.quantity * item.unit_price for item in self.items)
        return subtotal + self.tax_amount + self.shipping_amount - self.discount_amount

    def update_status(self, new_status):
        if isinstance(new_status, OrderStatus):
            self.status = new_status
        elif isinstance(new_status, str):
            self.status = OrderStatus(new_status)
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def update_payment_status(self, new_status):
        if isinstance(new_status, PaymentStatus):
            self.payment_status = new_status
        elif isinstance(new_status, str):
            self.payment_status = PaymentStatus(new_status)
        db.session.commit()

    def mark_as_completed(self):
        self.status = OrderStatus.DELIVERED
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def mark_as_cancelled(self):
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
        db.session.commit()

    def get_order_items_count(self):
        return sum(item.quantity for item in self.items)

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_sku = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<OrderItem {self.product_name} x {self.quantity}>'

    def get_subtotal(self):
        return self.quantity * self.unit_price

    @classmethod
    def create_from_cart_item(cls, cart_item, order_id):
        return cls(
            order_id=order_id,
            product_id=cart_item.product_id,
            product_name=cart_item.product.name,
            product_sku=cart_item.product.sku,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.get_current_price()
        )