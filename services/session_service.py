from time import time

from models.session import Session
from extensions import db


class SessionService:

    @staticmethod
    def new_session(session_name, owner_id, robt_id):

        # 创建新用户
        if not session_name:
            session_name = f"{robt_id}_{int(time())}"
        session = Session(session_name=session_name, owner_id=owner_id, robt_id=robt_id)
        db.session.add(session)
        db.session.commit()
        print(f"session.id:{session.id}")

        return session

    @staticmethod
    def get_session_by_id(session_id):
        return Session.query.get(session_id)

    @staticmethod
    def get_session_by_owner(owner_id):
        return Session.query.filter_by(owner_id=owner_id)