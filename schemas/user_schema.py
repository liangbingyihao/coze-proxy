from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class AuthSchema(Schema):
    access_token = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Str(dump_only=True)
