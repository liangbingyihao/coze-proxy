from datetime import datetime
from extensions import db
from utils.security import generate_password_hash,verify_password


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(50), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, index=True, nullable=False)
    robt_id = db.Column(db.Integer, index=True, nullable=False)
    tags = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, session_name, owner_id, robt_id):
        self.session_name = session_name
        self.owner_id = owner_id
        self.robt_id = robt_id

    def __repr__(self):
        return f'<session {self.owner_id} {self.session_name}>'