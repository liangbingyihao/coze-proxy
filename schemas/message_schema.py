from marshmallow import Schema, fields

class MessageSchema(Schema):
    id = fields.Int(dump_only=True)
    session_id = fields.Int(dump_only=True)
    context_id = fields.Int(dump_only=True)
    status = fields.Int(dump_only=True)
    action = fields.Int(dump_only=True)
    content = fields.Str()
    feedback = fields.Raw()
    feedback_text = fields.Str()
    created_at = fields.DateTime()