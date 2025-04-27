import logging
import time

from models.message import Message
from extensions import db
from models.session import Session
from services.coze_service import CozeService
from services.session_service import SessionService
from utils.exceptions import AuthError


class MessageService:

    @staticmethod
    def check_permission(session_id, owner_id):
        # session = SessionService.get_session_by_id(session_id)
        session = Session.query.filter_by(id=session_id).with_entities(Session.owner_id,Message.Session.session_name).one()
        # session_owner,session_name = session[0],session[1]
        if session[0] != owner_id:
            raise AuthError('session no permission', 404)
        return session

    @staticmethod
    def new_message(session_id, owner_id, content, context_id):
        session = MessageService.check_permission(session_id, owner_id)
        logging.debug(f"session:{session}")
        message = Message(session_id, content, context_id)
        db.session.add(message)
        db.session.commit()
        logging.warning(f"message.id:{message.id}")
        CozeService.chat_with_coze_async(owner_id,message.id)

        return message.id

    # @staticmethod
    # def get_session_by_id(session_id):
    #     return Session.query.get(session_id)

    @staticmethod
    def filter_message(owner_id, session_id, context_id, search, page, limit):
        session = MessageService.check_permission(session_id, owner_id)
        if context_id:
            return Message.query.filter_by(context_id=context_id)
        return Message.query.filter_by(session_id=session_id).paginate(page=page, per_page=limit, error_out=False)

    @staticmethod
    def filter_msg_by_context_id(owner_id, session_id, context_id):
        session = MessageService.check_permission(session_id, owner_id)
        return Message.query.filter_by(context_id=context_id)

    @staticmethod
    def call_llm():
        logging.warning("Task #1 start!")
        try:
            time.sleep(10)
        except Exception as e:
            logging.exception(e)
        logging.warning("Task #1 is done!")
