from datetime import datetime
from time import time

from sqlalchemy import desc, update, and_

from models.message import Message
from models.session import Session
from extensions import db
from services.coze_service import CozeService


class SessionService:

    @staticmethod
    def new_session(session_name, owner_id, robot_id):

        # 创建会话
        # if not session_name:
        #     session_name = f"{robt_id}_{int(time())}"
        session = Session.query.filter_by(owner_id=owner_id, session_name=session_name).first()
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
        return Session.query.filter_by(owner_id=owner_id, robot_id=0).order_by(desc(Session.updated_at)).paginate(
            page=page, per_page=limit, error_out=False)

    @staticmethod
    def reset_updated_at(session_id):
        if not session_id or session_id <= 0:
            return
        last_msg = Message.query.filter_by(session_id=session_id).order_by(desc(Message.id)).first()
        update_time = last_msg.created_at if last_msg else datetime(2025, 1, 1)
        Session.query.filter_by(id=session_id).update({
            "updated_at": update_time
        })
        db.session.commit()

    @staticmethod
    def del_session(owner_id, session_id):
        exits_session = Session.query.filter_by(id=session_id, owner_id=owner_id).first()

        if exits_session:
            # 执行删除
            db.session.delete(exits_session)
            db.session.commit()

        update_stmt = (
            update(Message)
            .where(
                and_(Message.owner_id == owner_id) &
                (Message.session_id == session_id)
            )
            .values(session_id=-1)
        )
        db.session.execute(update_stmt)
        db.session.commit()

    @staticmethod
    def set_session_name(owner_id,session_id,session_name):
        if not session_id or session_id <= 0:
            return
        session = Session.query.filter_by(id=session_id, owner_id=owner_id).first()
        if session:
            session.session_name = session_name
            db.session.commit()
            return True