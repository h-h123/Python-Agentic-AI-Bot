from src.extensions import db
from datetime import datetime
from src.models.base import BaseModel

class Product(db.Model, BaseModel):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image = db.Column(db.String(100))
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    sku = db.Column(db.String(50), unique=True)
    discount = db.Column(db.Numeric(5, 2), default=0.00)

    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    @property
    def discounted_price(self):
        return self.price * (1 - (self.discount / 100)) if self.discount > 0 else self.price

    @property
    def in_stock(self):
        return self.stock > 0

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity):
        self.stock += quantity
        self.save()

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"

    def to_dict(self):
        product_dict = super().to_dict()
        product_dict['discounted_price'] = str(self.discounted_price)
        product_dict['in_stock'] = self.in_stock
        return product_dict

class ProductCategory(db.Model, BaseModel):
    __tablename__ = 'product_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    is_active = db.Column(db.Boolean, default=True)

    parent = db.relationship('ProductCategory', remote_side=[id], backref='children')
    products = db.relationship('Product', backref='product_category', lazy=True)

    def __repr__(self):
        return f"ProductCategory('{self.name}')"

    def to_dict(self):
        category_dict = super().to_dict()
        category_dict.pop('parent_id', None)
        return category_dict