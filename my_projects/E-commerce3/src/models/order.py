from src.extensions import db
from datetime import datetime
from src.models.base import BaseModel
from enum import Enum

class OrderStatus(Enum):
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'
    REFUNDED = 'Refunded'

class Order(db.Model, BaseModel):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    billing_address = db.Column(db.Text)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')
    shipping_method = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0.00)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items)

    @property
    def grand_total(self):
        return self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount

    def update_status(self, new_status):
        if isinstance(new_status, OrderStatus):
            self.status = new_status
        elif new_status in [status.value for status in OrderStatus]:
            self.status = OrderStatus(new_status)
        else:
            raise ValueError(f"Invalid status: {new_status}")
        self.save()

    def add_item(self, product_id, quantity, price):
        existing_item = OrderItem.query.filter_by(
            order_id=self.id,
            product_id=product_id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = OrderItem(
                order_id=self.id,
                product_id=product_id,
                quantity=quantity,
                price=price
            )
            db.session.add(new_item)
        self.save()

    def calculate_totals(self):
        self.total_amount = self.grand_total
        self.save()

    def cancel(self):
        self.update_status(OrderStatus.CANCELLED)
        for item in self.items:
            product = item.product
            product.increase_stock(item.quantity)

    def __repr__(self):
        return f"Order('{self.order_number}', User: '{self.user_id}', Status: '{self.status.value}')"

    def to_dict(self):
        order_dict = super().to_dict()
        order_dict['status'] = self.status.value
        order_dict['subtotal'] = str(self.subtotal)
        order_dict['grand_total'] = str(self.grand_total)
        order_dict['order_date'] = self.order_date.isoformat()
        order_dict['items'] = [item.to_dict() for item in self.items]
        order_dict.pop('payment_status', None)
        return order_dict

class OrderItem(db.Model, BaseModel):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def subtotal(self):
        return self.quantity * self.price

    @property
    def product_name(self):
        return self.product.name if self.product else "Deleted Product"

    def __repr__(self):
        return f"OrderItem('{self.product_name}', Quantity: {self.quantity})"

    def to_dict(self):
        item_dict = super().to_dict()
        item_dict['subtotal'] = str(self.subtotal)
        item_dict['product_name'] = self.product_name
        if self.product:
            item_dict['product'] = {
                'id': self.product.id,
                'name': self.product.name,
                'image': self.product.image
            }
        return item_dict