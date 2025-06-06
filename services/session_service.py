from time import time

from sqlalchemy import desc

from models.session import Session
from extensions import db
from services.coze_service import CozeService


class SessionService:

    @staticmethod
    def new_session(session_name, owner_id, robot_id):

        # 创建会话
        # if not session_name:
        #     session_name = f"{robt_id}_{int(time())}"
        session = Session.query.filter_by(owner_id=owner_id,session_name=session_name).first()
        if session:
            return session
        session = Session(session_name=session_name, owner_id=owner_id, robot_id=robot_id)
        # session.conversation_id = CozeService.create_conversations()
        db.session.add(session)
        db.session.commit()
        print(f"session.id:{session.id}")

        return session

    @staticmethod
    def get_session_by_id(session_id):
        return Session.query.get(session_id)

    @staticmethod
    def get_session_by_owner(owner_id, page, limit):
        return Session.query.filter_by(owner_id=owner_id,robot_id=0).order_by(desc(Session.id)).paginate(page=page, per_page=limit, error_out=False)