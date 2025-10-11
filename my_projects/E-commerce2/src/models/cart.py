from src import db
from .base import BaseModel

class Cart(BaseModel):
    __tablename__ = 'carts'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Cart {self.id} for User {self.user_id}>'

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.items)

    def get_total_items(self):
        return sum(item.quantity for item in self.items)

    def clear(self):
        for item in self.items:
            item.delete()
        self.is_active = False
        self.save()
        return self

    def add_item(self, product, quantity=1):
        existing_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product.id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            return existing_item

        new_item = CartItem(
            cart_id=self.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price
        )
        new_item.save()
        return new_item

    def remove_item(self, product_id):
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()

        if item:
            item.delete()
        return item

    def update_item_quantity(self, product_id, quantity):
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product_id
        ).first()

        if item:
            if quantity <= 0:
                return self.remove_item(product_id)
            item.quantity = quantity
            item.save()
        return item

class CartItem(BaseModel):
    __tablename__ = 'cart_items'

    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f'<CartItem {self.product_id} in Cart {self.cart_id}>'

    def get_subtotal(self):
        return self.quantity * float(self.unit_price)

    def update_price(self):
        product = Product.query.get(self.product_id)
        if product:
            self.unit_price = product.price
            self.save()
        return self