import json

from marshmallow import Schema, fields, ValidationError


class JSONStringField(fields.Field):
    """将字符串字段序列化为JSON对象"""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        try:
            return json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON string: {str(e)}")

    def _deserialize(self, value, attr, data, **kwargs):
        # 反序列化时保持不变或根据需求处理
        return value

class MessageSchema(Schema):
    id = fields.Int(dump_only=True)
    session_id = fields.Int(dump_only=True)
    context_id = fields.Int(dump_only=True)
    status = fields.Int(dump_only=True)
    action = fields.Int(dump_only=True)
    content = fields.Str()
    feedback = JSONStringField()
    feedback_text = fields.Str()
    created_at = fields.DateTime()