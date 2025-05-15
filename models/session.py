import time

from extensions import db


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(50), index=True,nullable=False)
    owner_id = db.Column(db.Integer, index=True, nullable=False)
    robt_id = db.Column(db.Integer, index=True, nullable=False)
    tags = db.Column(db.String(255))
    conversation_id = db.Column(db.String(255))
    # 创建时间（自动设置）
    created_at = db.Column(db.Integer, default=lambda: int(time.time()))
    updated_at = db.Column(db.Integer, default=lambda: int(time.time()))

    # # 更新时间（自动更新）
    # updated_at = db.Column(
    #     TIMESTAMP,
    #     server_default=text('CURRENT_TIMESTAMP'),
    #     server_onupdate=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
    #     nullable=False
    # )
    # created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    # updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __init__(self, session_name, owner_id, robt_id):
        self.session_name = session_name or ""
        self.owner_id = owner_id
        self.robt_id = robt_id

    def __repr__(self):
        return f'<session {self.owner_id} {self.session_name}>'