from marshmallow import Schema, fields, validate, pre_load, post_load, validates_schema, ValidationError
from datetime import datetime
from src.models.product import Product, ProductCategory

class ProductCategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=50))
    description = fields.String(allow_none=True)
    parent_id = fields.Integer(allow_none=True)
    is_active = fields.Boolean(default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_load
    def make_category(self, data, **kwargs):
        return ProductCategory(**data)

class ProductSchema(Schema):
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
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    category = fields.Nested(ProductCategorySchema, dump_only=True)

    @post_load
    def make_product(self, data, **kwargs):
        return Product(**data)

class ProductSearchSchema(Schema):
    q = fields.String(required=True, validate=validate.Length(min=1, max=100))
    page = fields.Integer(validate=validate.Range(min=1), default=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), default=10)

class ProductFilterSchema(Schema):
    category_id = fields.Integer(allow_none=True)
    min_price = fields.Decimal(as_string=True, allow_none=True, places=2)
    max_price = fields.Decimal(as_string=True, allow_none=True, places=2)
    in_stock = fields.Boolean(allow_none=True)
    page = fields.Integer(validate=validate.Range(min=1), default=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), default=10)

class BulkProductUpdateSchema(Schema):
    product_ids = fields.List(fields.Integer(), required=True)
    updates = fields.Dict(required=True, keys=fields.String(), values=fields.Raw())

    @validates_schema
    def validate_updates(self, data, **kwargs):
        valid_fields = {'price', 'stock', 'is_active', 'discount'}
        for field in data['updates'].keys():
            if field not in valid_fields:
                raise ValidationError(f"Invalid field: {field}", field)