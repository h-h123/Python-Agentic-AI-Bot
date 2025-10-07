from datetime import datetime
from . import db

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Cart {self.id}>'

    def add_item(self, product, quantity=1):
        existing_item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product.id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = CartItem(
                cart_id=self.id,
                product_id=product.id,
                quantity=quantity
            )
            db.session.add(new_item)
        db.session.commit()

    def remove_item(self, product):
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product.id
        ).first()

        if item:
            db.session.delete(item)
            db.session.commit()

    def update_item_quantity(self, product, quantity):
        item = CartItem.query.filter_by(
            cart_id=self.id,
            product_id=product.id
        ).first()

        if item:
            if quantity <= 0:
                self.remove_item(product)
            else:
                item.quantity = quantity
                db.session.commit()

    def clear(self):
        CartItem.query.filter_by(cart_id=self.id).delete()
        db.session.commit()

    def get_total_price(self):
        return sum(item.product.get_current_price() * item.quantity for item in self.items)

    def get_total_items(self):
        return sum(item.quantity for item in self.items)

    def get_item_count(self):
        return len(self.items)

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_item'),
    )

    def __repr__(self):
        return f'<CartItem {self.product_id} x {self.quantity}>'

    def get_subtotal(self):
        return self.product.get_current_price() * self.quantity