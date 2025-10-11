from marshmallow import Schema, fields, validate, pre_load, post_load, validates_schema, ValidationError
from datetime import datetime
from src.models.user import User

class UserRegistrationSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    first_name = fields.String(validate=validate.Length(max=50))
    last_name = fields.String(validate=validate.Length(max=50))

    @validates_schema
    def validate_unique_fields(self, data, **kwargs):
        if User.query.filter_by(username=data['username']).first():
            raise ValidationError("Username already exists", "username")
        if User.query.filter_by(email=data['email']).first():
            raise ValidationError("Email already exists", "email")

    @post_load
    def create_user(self, data, **kwargs):
        return User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    remember = fields.Boolean(default=False)

class UserProfileSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(validate=validate.Length(max=50))
    email = fields.Email()
    first_name = fields.String(validate=validate.Length(max=50))
    last_name = fields.String(validate=validate.Length(max=50))
    phone_number = fields.String(validate=validate.Length(max=20))
    shipping_address = fields.String()
    billing_address = fields.String()
    is_admin = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    full_name = fields.String(dump_only=True)

    @post_load
    def update_user(self, data, **kwargs):
        user = kwargs.get('obj') if 'obj' in kwargs else User()
        for key, value in data.items():
            if value is not None:
                setattr(user, key, value)
        return user

class PasswordChangeSchema(Schema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=6))
    confirm_password = fields.String(required=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data['new_password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match", "confirm_password")

class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True)

class PasswordResetSchema(Schema):
    password = fields.String(required=True, validate=validate.Length(min=6))
    confirm_password = fields.String(required=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data['password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match", "confirm_password")

class UserAdminSchema(UserProfileSchema):
    is_admin = fields.Boolean()

class UserListSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.Email()
    full_name = fields.String()
    is_admin = fields.Boolean()
    created_at = fields.DateTime()