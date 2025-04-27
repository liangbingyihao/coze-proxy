import logging
import os
from functools import lru_cache

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, scoped_session
from concurrent.futures import ThreadPoolExecutor

coze_api_token = os.getenv("COZE_API_TOKEN")
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL, COZE_COM_BASE_URL  # noqa

import logging

# 创建日志记录器
logger = logging.getLogger('my_app')
logger.setLevel(logging.DEBUG)  # 设置日志级别

# 创建文件处理器
file_handler = logging.FileHandler('coze.log')
file_handler.setLevel(logging.INFO)

# 创建日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(file_handler)

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)

# 第一步：生成engine对象
engine = create_engine(
    os.getenv("DATABASE_URL"),
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=3600  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)
# 第二步：拿到一个Session类,传入engine
DBSession = sessionmaker(bind=engine)

class CozeService:
    bot_id = "7481241756508504091"
    executor = ThreadPoolExecutor(3)


    @staticmethod
    def chat_with_coze_async(user_id, context_id,conversation_id):
        try:
            logger.info(f"chat_with_coze_async: {user_id, context_id,conversation_id}")
            CozeService.executor.submit(CozeService.chat_with_coze, user_id, context_id,conversation_id)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def chat_with_coze(user_id, context_id,conversation_id):
        session = None
        from models.message import Message
        try:
            session = DBSession()
            message = session.query(Message).filter_by(id=context_id, status=0).with_entities(Message.content,
                                                                                              Message.session_id).one()
        except exc.OperationalError as e:
            session.rollback()
            logger.exception(e)
            engine.dispose()
            session = DBSession()
            message = session.query(Message).filter_by(id=context_id, status=0).with_entities(Message.content,
                                                                                              Message.session_id).one()
        except Exception as e:
            logger.exception(e)
            return

        try:

            # from models.session import Session
            # coze_session = session.query(Session).filter_by(id=message.session_id).one()
            # logger.warning(f"start: {user_id, context_id, message, user, coze_session}")
            # # session_name, conversation_id = thread.session_name, thread.conversation_id
            # if not coze_session.conversation_id:
            #     conversation_id = CozeService.create_conversations()
            #     logger.warning(f"create_conversations: {conversation_id}")
            #     coze_session.conversation_id = conversation_id
            #     session.commit()

            rsp_msg = Message(message[1], "(回应生成中)", context_id, 1)
            session.add(rsp_msg)
            session.commit()

            response = CozeService._chat_with_coze(session, conversation_id, rsp_msg, user_id, message[0])
            if response:
                rsp_msg.content = response
                rsp_msg.status = 2
                # rsp_msg = Message(message[1], response,context_id,1)
                # session.add(rsp_msg)
                session.commit()
                logger.warning(f"GOT: {response}")
        except Exception as e:
            logger.exception(e)
        # finally:
        #     if session:
        #         session.close()  # 重要！清理会话

    @staticmethod
    def create_conversations():
        conversation = coze.conversations.create()
        return conversation.id

    @staticmethod
    def _chat_with_coze(session, conversation_id, ori_msg, user_id, msg):
        all_content = ""
        for event in coze.chat.stream(
                bot_id=CozeService.bot_id,
                user_id=user_id,
                additional_messages=[Message.build_user_question_text(msg)],
                conversation_id=conversation_id
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                message = event.message
                all_content += message.content
                ori_msg.content = all_content + "(回应生成中...)"
                session.commit()
                # print(f"role={message.role}, content={message.content}")
        return all_content
