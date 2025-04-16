from datetime import datetime
from extensions import db


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, index=True, nullable=False)
    context_id = db.Column(db.Integer, index=True, nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, session_id, content,context_id):
        self.session_id = session_id
        self.content = content
        self.context_id =context_id

    def __repr__(self):
        return f'<message {self.id}>'