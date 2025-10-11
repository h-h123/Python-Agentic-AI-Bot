from marshmallow import Schema, fields, validate, pre_load, post_load, validates_schema, ValidationError
from datetime import datetime
from src.models.order import Order, OrderItem, OrderStatus
from src.models.product import Product
from src.models.user import User

class OrderItemSchema(Schema):
    id = fields.Integer(dump_only=True)
    order_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    price = fields.Decimal(as_string=True, required=True, places=2)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    product = fields.Nested('ProductSchema', dump_only=True)
    subtotal = fields.Decimal(as_string=True, dump_only=True, places=2)
    product_name = fields.String(dump_only=True)

    @post_load
    def make_order_item(self, data, **kwargs):
        return OrderItem(**data)

class OrderSchema(Schema):
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
    user = fields.Nested('UserSchema', dump_only=True, exclude=('password_hash',))

    @post_load
    def make_order(self, data, **kwargs):
        return Order(**data)

class OrderCreateSchema(Schema):
    shipping_address = fields.String(required=True)
    billing_address = fields.String(allow_none=True)
    payment_method = fields.String(required=True, validate=validate.Length(max=50))
    shipping_method = fields.String(validate=validate.Length(max=50))
    notes = fields.String(allow_none=True)

    @validates_schema
    def validate_shipping(self, data, **kwargs):
        if data.get('shipping_method') not in ['standard', 'express']:
            raise ValidationError("Invalid shipping method", "shipping_method")

class OrderUpdateSchema(Schema):
    status = fields.Enum(OrderStatus, by_value=True)
    tracking_number = fields.String(validate=validate.Length(max=100))
    shipping_method = fields.String(validate=validate.Length(max=50))
    notes = fields.String(allow_none=True)

class OrderStatusUpdateSchema(Schema):
    status = fields.Enum(OrderStatus, by_value=True, required=True)

class OrderFilterSchema(Schema):
    status = fields.Enum(OrderStatus, by_value=True, allow_none=True)
    user_id = fields.Integer(allow_none=True)
    date_from = fields.DateTime(allow_none=True)
    date_to = fields.DateTime(allow_none=True)
    page = fields.Integer(validate=validate.Range(min=1), default=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), default=10)

class OrderSummarySchema(Schema):
    order_number = fields.String()
    order_date = fields.DateTime()
    status = fields.Enum(OrderStatus, by_value=True)
    total_amount = fields.Decimal(as_string=True, places=2)
    items_count = fields.Integer()
    grand_total = fields.Decimal(as_string=True, places=2)