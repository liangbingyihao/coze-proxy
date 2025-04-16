from time import time

from models.message import Message
from models.session import Session
from extensions import db
from services.session_service import SessionService
from utils.exceptions import AuthError


class MessageService:

    @staticmethod
    def check_permission(session_id, owner_id):
        session = SessionService.get_session_by_id(session_id)
        if session.owner_id != owner_id:
            raise AuthError('session no permission', 404)
        return session

    @staticmethod
    def new_message(session_id, owner_id, content, context_id):
        session = MessageService.check_permission(session_id, owner_id)
        print(f"session:{session.session_name,session.robt_id}")
        message = Message(session_id, content, context_id)
        db.session.add(message)
        db.session.commit()
        print(f"message.id:{message.id}")

        return message.id

    # @staticmethod
    # def get_session_by_id(session_id):
    #     return Session.query.get(session_id)

    @staticmethod
    def filter_message(owner_id,session_id,search,page,limit):
        session = MessageService.check_permission(session_id, owner_id)
        return Message.query.filter_by(session_id=session_id).ilter(Message.content.contains(search)).paginate(page=page, per_page=limit)
