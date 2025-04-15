from marshmallow import Schema, fields

class SessionSchema(Schema):
    owner_id = fields.Int(dump_only=True)
    robt_id = fields.Int(dump_only=True)
    session_name = fields.Str()
    tags = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.Str()