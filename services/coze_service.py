import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from extensions import db

coze_api_token = os.getenv("COZE_API_TOKEN")

from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL,COZE_COM_BASE_URL  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)


class CozeService:
    bot_id = "7481241756508504091"
    executor = ThreadPoolExecutor(3)

    @staticmethod
    def chat_with_coze_async(user_id, context_id):
        try:
            logging.warning(f"chat_with_coze_async: {user_id, context_id}")
            CozeService.executor.submit(CozeService.chat_with_coze, user_id, context_id)
        except Exception as e:
            logging.exception(e)

    @staticmethod
    def chat_with_coze(user_id, context_id):
        session = None
        try:
            session = db.create_scoped_session()
            from models.message import Message
            from models.user import User
            message = Message.query.filter_by(id=context_id, status=0).with_entities(Message.content).one()
            user = User.query.filter_by(id=user_id).with_entities(User.username).one()
            logging.warning(f"GOT: {user_id, context_id, message, user}")
        except Exception as e:
            logging.exception(e)
        finally:
            if session:
                session.remove()  # 重要！清理会话

    @staticmethod
    def _chat_with_coze(cls, user_id, msg):
        all_content = ""
        for event in coze.chat.stream(
                bot_id=cls.bot_id, user_id=user_id, additional_messages=[Message.build_user_question_text(msg)]
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                message = event.message
                all_content += message.content
                # print(f"role={message.role}, content={message.content}")
        return all_content
