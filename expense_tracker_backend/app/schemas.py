from marshmallow import Schema, fields, validate


class PaginationSchema(Schema):
    total = fields.Int()
    total_pages = fields.Int()
    first_page = fields.Int()
    last_page = fields.Int()
    page = fields.Int()
    previous_page = fields.Int(allow_none=True)
    next_page = fields.Int(allow_none=True)


class MessageSchema(Schema):
    message = fields.Str(required=True)


# Auth schemas
class RegisterRequestSchema(Schema):
    email = fields.Email(required=True, description="User email")
    password = fields.Str(required=True, validate=validate.Length(min=6), load_only=True)
    name = fields.Str(required=False, allow_none=True)


class LoginRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class AuthResponseSchema(Schema):
    access_token = fields.Str(required=True, description="JWT access token")


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email()
    name = fields.Str(allow_none=True)


# Category schemas
class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    color = fields.Str(required=False, allow_none=True)


class CategoryUpdateSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(min=1, max=120))
    color = fields.Str(required=False, allow_none=True)


class CategorySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    color = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


# Expense schemas
class ExpenseCreateSchema(Schema):
    amount = fields.Decimal(required=True, as_string=True)
    currency = fields.Str(required=False, missing="USD")
    description = fields.Str(required=False, allow_none=True)
    date = fields.DateTime(required=False)
    category_id = fields.Int(required=False, allow_none=True)


class ExpenseUpdateSchema(Schema):
    amount = fields.Decimal(required=False, as_string=True)
    currency = fields.Str(required=False)
    description = fields.Str(required=False, allow_none=True)
    date = fields.DateTime(required=False)
    category_id = fields.Int(required=False, allow_none=True)


class ExpenseSchema(Schema):
    id = fields.Int()
    amount = fields.Decimal(as_string=True)
    currency = fields.Str()
    description = fields.Str(allow_none=True)
    date = fields.DateTime()
    category_id = fields.Int(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
