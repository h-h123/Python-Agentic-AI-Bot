from marshmallow import Schema, fields, validate, pre_load, post_load, validates_schema, ValidationError
from datetime import datetime
from src.models.product import Product, ProductCategory
from src.models.user import User
from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderItem, OrderStatus

class BaseSchema(Schema):
    """Base schema with common fields and methods"""
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ProductCategorySchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=50))
    description = fields.String(allow_none=True)
    parent_id = fields.Integer(allow_none=True)
    is_active = fields.Boolean(default=True)

    @post_load
    def make_category(self, data, **kwargs):
        return ProductCategory(**data)

class ProductSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=100))
    description = fields.String(allow_none=True)
    price = fields.Decimal(as_string=True, required=True, places=2)
    stock = fields.Integer(required=True, validate=validate.Range(min=0))
    image = fields.String(allow_none=True)
    category_id = fields.Integer(allow_none=True)
    is_active = fields.Boolean(default=True)
    sku = fields.String(validate=validate.Length(max=50))
    discount = fields.Decimal(as_string=True, places=2, default=0.00)
    discounted_price = fields.Decimal(as_string=True, dump_only=True)
    in_stock = fields.Boolean(dump_only=True)
    category = fields.Nested(ProductCategorySchema, dump_only=True)

    @post_load
    def make_product(self, data, **kwargs):
        return Product(**data)

class UserSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(max=50))
    email = fields.Email(required=True)
    first_name = fields.String(validate=validate.Length(max=50))
    last_name = fields.String(validate=validate.Length(max=50))
    is_admin = fields.Boolean(default=False)
    phone_number = fields.String(validate=validate.Length(max=20))
    shipping_address = fields.String(allow_none=True)
    billing_address = fields.String(allow_none=True)
    full_name = fields.String(dump_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

class CartItemSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    cart_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    product = fields.Nested(ProductSchema, dump_only=True)
    subtotal = fields.Decimal(as_string=True, dump_only=True, places=2)

    @post_load
    def make_cart_item(self, data, **kwargs):
        return CartItem(**data)

class CartSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    is_active = fields.Boolean(default=True)
    items = fields.Nested(CartItemSchema, many=True, dump_only=True)
    total_items = fields.Integer(dump_only=True)
    total_price = fields.Decimal(as_string=True, dump_only=True, places=2)

    @post_load
    def make_cart(self, data, **kwargs):
        return Cart(**data)

class OrderItemSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    order_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    price = fields.Decimal(as_string=True, required=True, places=2)
    product = fields.Nested(ProductSchema, dump_only=True)
    subtotal = fields.Decimal(as_string=True, dump_only=True, places=2)
    product_name = fields.String(dump_only=True)

    @post_load
    def make_order_item(self, data, **kwargs):
        return OrderItem(**data)

class OrderSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    order_number = fields.String(dump_only=True)
    order_date = fields.DateTime(dump_only=True)
    status = fields.Enum(OrderStatus, by_value=True, dump_only=True)
    total_amount = fields.Decimal(as_string=True, required=True, places=2)
    shipping_address = fields.String(required=True)
    billing_address = fields.String(allow_none=True)
    payment_method = fields.String(required=True, validate=validate.Length(max=50))
    payment_status = fields.String(dump_only=True)
    shipping_method = fields.String(validate=validate.Length(max=50))
    tracking_number = fields.String(validate=validate.Length(max=100))
    notes = fields.String(allow_none=True)
    tax_amount = fields.Decimal(as_string=True, default=0.00, places=2)
    shipping_cost = fields.Decimal(as_string=True, default=0.00, places=2)
    discount_amount = fields.Decimal(as_string=True, default=0.00, places=2)
    subtotal = fields.Decimal(as_string=True, dump_only=True, places=2)
    grand_total = fields.Decimal(as_string=True, dump_only=True, places=2)
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)

    @post_load
    def make_order(self, data, **kwargs):
        return Order(**data)