from sqlalchemy import text, TIMESTAMP, Index, UniqueConstraint

from extensions import db


class Favorites(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, index=True, nullable=False)
    message_id = db.Column(db.Integer, index=True, nullable=False)
    content_type = db.Column(db.Integer, index=True, nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)
    # 创建时间（自动设置）
    created_at = db.Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP'),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint('message_id', 'content_type', name='uq_msg'),
        {'extend_existing': True}
        # 可以添加多个唯一约束
        # UniqueConstraint('email', name='uq_email')
    )

    # # 更新时间（自动更新）
    # updated_at = db.Column(
    #     TIMESTAMP,
    #     server_default=text('CURRENT_TIMESTAMP'),
    #     server_onupdate=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
    #     nullable=False
    # )
    # created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    # updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __init__(self,owner_id, message_id,  content_type,content):
        self.owner_id = owner_id
        self.message_id = message_id
        self.content_type = content_type
        self.content = content

    def __repr__(self):
        return f'<favorites {self.message_id} {self.content_type}>'