from src.extensions import db
from datetime import datetime
from src.models.base import BaseModel

class Cart(db.Model, BaseModel):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)

    def clear(self):
        for item in self.items:
            item.delete()
        self.is_active = False
        self.save()

    def add_item(self, product_id, quantity=1):
        existing_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            new_item = CartItem(
                cart_id=self.id,
                product_id=product_id,
                quantity=quantity
            )
            new_item.save()

    def remove_item(self, product_id):
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()

        if item:
            item.delete()

    def update_item_quantity(self, product_id, quantity):
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()

        if item:
            if quantity <= 0:
                self.remove_item(product_id)
            else:
                item.quantity = quantity
                item.save()

    def __repr__(self):
        return f"Cart('{self.id}', User: '{self.user_id}', Items: {self.total_items})"

    def to_dict(self):
        cart_dict = super().to_dict()
        cart_dict['total_price'] = str(self.total_price)
        cart_dict['total_items'] = self.total_items
        cart_dict['items'] = [item.to_dict() for item in self.items]
        return cart_dict

class CartItem(db.Model, BaseModel):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    @property
    def subtotal(self):
        return self.quantity * self.product.discounted_price

    def __repr__(self):
        return f"CartItem('{self.product.name}', Quantity: {self.quantity})"

    def to_dict(self):
        item_dict = super().to_dict()
        item_dict['product'] = self.product.to_dict()
        item_dict['subtotal'] = str(self.subtotal)
        return item_dict