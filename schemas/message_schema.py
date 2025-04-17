from marshmallow import Schema, fields

class MessageSchema(Schema):
    #id | session_id | context_id | content   | created_at
    id = fields.Int(dump_only=True)
    session_id = fields.Int(dump_only=True)
    context_id = fields.Int(dump_only=True)
    status = fields.Int(dump_only=True)
    content = fields.Str()
    created_at = fields.DateTime()