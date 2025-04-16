from marshmallow import Schema, fields

class SessionSchema(Schema):
    #id | session_id | context_id | content   | created_at
    id = fields.Int(dump_only=True)
    owner_id = fields.Int(dump_only=True)
    robt_id = fields.Int(dump_only=True)
    session_name = fields.Str()
    tags = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.Str()