import json
import os
from sqlalchemy import create_engine, exc, desc
from sqlalchemy.orm import sessionmaker
from concurrent.futures import ThreadPoolExecutor

coze_api_token = os.getenv("COZE_API_TOKEN")
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL, COZE_COM_BASE_URL, MessageType  # noqa

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

msg_feedback = '''你要帮助基督徒用户记录的感恩小事，圣灵感动，亮光发现等信息进行以下反馈:
                1.bible:返回一段基督教新教的圣经中的相关经文进行鼓励
                2.view:并针对该经文予一段100字左右的内容拓展。
                3.event:从输入内容里提取出发生的事件，5个字以内。优先选用这些事件：${event}。实在不匹配再新增事件返回
                4.tag:对用户输入的内容进行打标签，标签优先使用："感恩，赞美，祈求，认罪，发现，代祷，心情，懊悔"，没有匹配标签可以新增标签
                5.summary:给出8个字以内的重点小结
                6.explore:给出2个和用户输入内容密切相关的，引导基督教新教教义范围内进一步展开讨论的话题，话题的形式可以是问题或者指令。
                7.严格按json格式返回。{"bible":<bible>,"view":<view>,"explore":<explore>,"event":<event>,"tag":<tag>,"summary":<summary>}
                8.对于跟信仰，圣经无关任何输入，如吃喝玩乐推荐、或者毫无意义的文本，只需要回复""。
                以下是用户的输入内容：
                '''

msg_explore = '''你要在基督教正统教义范围内对下面的输入进行回应，回应内容200字以内:
                 用户问题:${question}
                '''

msg_error = '''我很乐意帮你做大小事情的记录，都会成为你看见上帝恩典的点点滴滴。但这个问题我暂时没有具体的推荐，你有此刻想记录的心情或亮光想记录吗？
'''

class CozeService:
    bot_id = "7481241756508504091"
    executor = ThreadPoolExecutor(3)

    @staticmethod
    def chat_with_coze_async(user_id,msg_id):
        '''
        :param user_id:
        :param context_id:
        :param msg_id: 1 用户正常记录；其他 用户探索
        :return:
        '''
        try:
            logger.info(f"chat_with_coze_async: {user_id, msg_id}")
            CozeService.executor.submit(CozeService.chat_with_coze, user_id, msg_id)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def chat_with_coze(user_id, context_id):
        session = None
        from models.message import Message
        try:
            session = DBSession()
            message = session.query(Message).filter_by(id=context_id, status=0).first()
        except exc.OperationalError as e:
            session.rollback()
            logger.exception(e)
            engine.dispose()
            session = DBSession()
            message = session.query(Message).filter_by(id=context_id, status=0).first()
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
            message.status=1
            session.commit()
            session_lst = []
            from models.session import Session
            if message.context_id:
                # 用户探索类型
                # context_msg = session.query(Message).filter_by(id=message.context_id).first()
                # ask_msg = msg_explore.replace("${context}", context_msg.content)
                ask_msg = msg_explore.replace("${question}", message.content)
                # rsp_msg = message
            else:
                # rsp_msg = Message(0, user_id, "", context_id, 1)
                # session.add(rsp_msg)
                # session.commit()
                session_lst = session.query(Session).filter_by(owner_id=user_id).order_by(desc(Session.id)).with_entities(Session.id, Session.session_name).limit(100).all()
                names = "["
                for session_id, session_name in session_lst:
                    names += f"\"{session_name}\","
                names+="]"
                ask_msg = msg_feedback.replace("${event}", names)
                ask_msg += message.content

            # if message.action == 0:
            #     from models.session import Session
            #     session_lst = session.query(Session).filter_by(owner_id=user_id).order_by(
            #         desc(Session.id)).with_entities(Session.id, Session.session_name).limit(50).all()
            #     names = ""
            #     for session_id, session_name in session_lst:
            #         names += f"{session_name},"
            #     ask_msg = msg_feedback.replace("${event}", names)
            #     ask_msg += message.content
            # else:
            #     ask_msg = message.content

            response = CozeService._chat_with_coze(session, message, user_id, ask_msg)
            if response:
                logger.warning(f"GOT: {response}")
                try:
                    if not message.context_id and not message.session_id:
                        result = json.loads(response)
                        summary = result.get("summary")
                        bible,view = result.get('bible'),result.get('view')
                        if bible and view:
                            message.feedback_text=f"经文:{result.get('bible')}\n扩展:{result.get('view')}"
                        for session_id, session_name in session_lst:
                            if summary == session_name:
                                message.session_id = session_id
                                break
                        if not message.session_id and summary:
                            new_session = Session(summary, user_id, 0)
                            session.add(new_session)
                            session.commit()
                            message.session_id = new_session.id
                except Exception as e:
                    logger.exception(e)
                if message.context_id:
                    message.feedback_text = response
                else:
                    message.feedback = response
                message.status = 2
                session.commit()

            # if need_summary:
            #     summary = CozeService._summary_by_coze(conversation_id, user_id)
            #     if summary:
            #         from models.session import Session
            #         session.query(Session).filter_by(id=message.session_id).update({"session_name": summary})
            #         session.commit()
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
    def _extract_content(text,s):
        import re
        s1,e1, s2, e2 = s
        bible, detail = "",""

        if not s1:
            match = re.search(r"(\"bible\"\s*:\s*)", text)
            if match:
                s[0] = s1 = match.end()

        if not s2:
            match = re.search(r"(\"view\"\s*:\s*)", text)
            if match:
                s[1] = e1 = match.start()
                s[2] = s2 = match.end()

        if not e2:
            match = re.search(r"(\"explore\"\s*:\s*)", text)
            if match:
                s[3] = e2 = match.start()
        if s1:
            bible = text[s1:e1 if e1 > 0 else -1]
        if s2:
            detail  = text[s2:e2 if e2 > 0 else -1]
        return bible, detail


    @staticmethod
    def _chat_with_coze(session, ori_msg, user_id, msg):
        all_content = ""
        pos = [0, 0, 0,0]
        logger.info(f"_chat_with_coze: {user_id, msg}")
        for event in coze.chat.stream(
                bot_id=CozeService.bot_id,
                user_id=str(user_id),
                additional_messages=[Message.build_user_question_text(msg)],
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                message = event.message
                all_content += message.content
                if not ori_msg.context_id:
                    if pos[3]<=0:
                        bible, detail = CozeService._extract_content(all_content,pos)
                        if bible:
                            bible = f"经文:{bible}\n"
                        if detail:
                            detail = f"扩展:{detail}"
                        ori_msg.feedback_text = f"{bible}{detail}"
                else:
                    ori_msg.feedback_text = all_content
                # logger.info(f"CONVERSATION_MESSAGE_DELTA: {ori_msg.feedback}")
                ori_msg.status = 1
                session.commit()
            elif event.event == ChatEventType.CONVERSATION_MESSAGE_COMPLETED and event.message.type==MessageType.ANSWER:
                # logger.info(f"CONVERSATION_MESSAGE_COMPLETED: {event.message.content}")
                return event.message.content
            # elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
            #     logger.info(f"CONVERSATION_CHAT_COMPLETED: {event.chat.usage.token_count}")
                # if event.message.content.startswith("{"):
                #     continue
                # msg_list.append(event.message.content)

    @staticmethod
    def _summary_by_coze(conversation_id, user_id):
        logger.info(f"_summary_by_coze: {user_id, conversation_id}")
        for event in coze.chat.stream(
                bot_id=CozeService.bot_id,
                user_id=str(user_id),
                additional_messages=[Message.build_user_question_text("10个字内描述本会话的主题")],
                conversation_id=conversation_id
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_COMPLETED:
                logger.info(f"_summary_by_coze got: {conversation_id, event.message.content}")
                return event.message.content
