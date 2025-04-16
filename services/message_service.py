from time import time

from models.message import Message
from models.session import Session
from extensions import db


class MessageService:

    @staticmethod
    def new_message(session_id, owner_id, content,context_id):
        message = Message(session_id, owner_id, content,context_id)
        db.session.add(message)
        db.session.commit()
        print(f"message.id:{message.id}")

        return message.id

    # @staticmethod
    # def get_session_by_id(session_id):
    #     return Session.query.get(session_id)

    @staticmethod
    def get_message_by_session(owner_id):
        return Session.query.filter_by(owner_id=owner_id)