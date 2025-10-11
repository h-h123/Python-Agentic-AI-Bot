from src import db
from .base import BaseModel
from enum import Enum
from datetime import datetime

class OrderStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class Order(BaseModel):
    __tablename__ = 'orders'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_address = db.Column(db.Text, nullable=False)
    billing_address = db.Column(db.Text, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    shipping_method = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.order_number} by User {self.user_id}>'

    def calculate_total(self):
        subtotal = sum(item.get_subtotal() for item in self.items)
        self.total_amount = subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        self.save()
        return self.total_amount

    def add_item(self, product, quantity, unit_price):
        existing_item = OrderItem.query.filter_by(
            order_id=self.id,
            product_id=product.id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            return existing_item

        new_item = OrderItem(
            order_id=self.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price
        )
        new_item.save()
        self.calculate_total()
        return new_item

    def update_status(self, new_status):
        if isinstance(new_status, str):
            new_status = OrderStatus(new_status)
        self.status = new_status
        self.save()
        return self.status

    def cancel(self):
        return self.update_status(OrderStatus.CANCELLED)

    def mark_as_shipped(self, tracking_number=None):
        self.update_status(OrderStatus.SHIPPED)
        if tracking_number:
            self.tracking_number = tracking_number
            self.save()
        return self.status

    def mark_as_delivered(self):
        return self.update_status(OrderStatus.DELIVERED)

    def get_order_summary(self):
        return {
            'order_number': self.order_number,
            'status': self.status.value,
            'total_amount': float(self.total_amount),
            'item_count': sum(item.quantity for item in self.items),
            'created_at': self.created_at.isoformat()
        }

class OrderItem(BaseModel):
    __tablename__ = 'order_items'

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f'<OrderItem {self.product_id} in Order {self.order_id}>'

    def get_subtotal(self):
        return self.quantity * float(self.unit_price)