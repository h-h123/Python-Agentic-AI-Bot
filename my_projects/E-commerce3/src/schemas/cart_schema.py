from marshmallow import Schema, fields, validate, pre_load, post_load, validates_schema, ValidationError
from datetime import datetime
from src.models.cart import Cart, CartItem
from src.models.product import Product

class CartItemSchema(Schema):
    id = fields.Integer(dump_only=True)
    cart_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    product = fields.Nested('ProductSchema', dump_only=True)
    subtotal = fields.Decimal(as_string=True, dump_only=True, places=2)

    @post_load
    def make_cart_item(self, data, **kwargs):
        return CartItem(**data)

class CartSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    is_active = fields.Boolean(default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    items = fields.Nested(CartItemSchema, many=True, dump_only=True)
    total_items = fields.Integer(dump_only=True)
    total_price = fields.Decimal(as_string=True, dump_only=True, places=2)

    @post_load
    def make_cart(self, data, **kwargs):
        return Cart(**data)

class AddToCartSchema(Schema):
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))

    @validates_schema
    def validate_product(self, data, **kwargs):
        product = Product.get_by_id(data['product_id'])
        if not product:
            raise ValidationError("Product not found", "product_id")
        if not product.in_stock:
            raise ValidationError("Product is out of stock", "product_id")
        if data['quantity'] > product.stock:
            raise ValidationError(f"Not enough stock. Only {product.stock} available", "quantity")

class UpdateCartItemSchema(Schema):
    quantity = fields.Integer(required=True, validate=validate.Range(min=0))

class CartSummarySchema(Schema):
    total_items = fields.Integer()
    total_price = fields.Decimal(as_string=True, places=2)
    items = fields.Nested(CartItemSchema, many=True)