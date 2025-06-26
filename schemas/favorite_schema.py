from marshmallow import Schema, fields

class FavoriteSchema(Schema):
    id = fields.Int(dump_only=True)
    message_id = fields.Str(dump_only=True)
    content_type = fields.Int(dump_only=True)
    content = fields.Str()
    created_at = fields.DateTime()