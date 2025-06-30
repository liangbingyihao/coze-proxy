import json
import os
from sqlalchemy import create_engine, exc, desc, func
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

logger.handlers.clear()
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

msg_json='''
!!!你必须根据用户使用的语言进行回复!!!

## 输出格式说明:
!!!本次输出需要生成一个严格符合 JSON 格式的字符串,不要包含 JSON 之外的任何字符（如注释或说明）。
其中字段`view`是一段 Markdown 格式的文本（需转义所有 JSON 特殊字符）,确保所有双引号（`"`）、反斜杠（`\`）、换行符（`\n`）等被转义为 `\"`、`\\`、`\\n`。
字段`view`格式要求：
1. Markdown 内容需包含标题、代码块和列表。
2. 确保所有双引号（`"`）、反斜杠（`\`）、换行符（`\n`）等被转义为 `\"`、`\\`、`\\n`。
3. view里面所有圣经经文全文要用**包裹加粗效果。例如：**“你们要将一切的忧虑卸给神，因为他顾念你们。”（彼前5:7）** 
4. 你必须根据用户使用的语言进行回复。

###以下是任务说明:

'''

msg_feedback = '''你要帮助基督徒用户记录的感恩小事，圣灵感动，亮光发现、回答用户关于信仰的问题，请进行以下反馈:
                1.view: 用户查看的回应文本,必须是**Markdown 格式的字符串**（支持标题、列表、代码块等语法）。详细说明见后面view字段的详细要求。
                2.bible:view字段回应包含的最主要的一节圣经经文，要包括经文全文和出处。例如“你们要将一切的忧虑卸给神，因为他顾念你们。”（彼前5:7）
                3.topic1:如果用户输入是关于信仰的问题，返回"信仰问答"，否则从${event}里选出一个主题分类,无法选取则为""
                3.topic2:无法选出topic1时，新增一个6个字以内的主题分类
                4.tag:对用户输入的内容返回的圣经经文打标签，标签只能从"信靠，盼望，刚强，光明，慈爱，喜乐，安慰，永恒，平安，恩典"选择最接近的一个。
                5.summary:给出8个字以内的重点小结
                6.explore:给出1个和用户输入内容密切相关的，引导基督教新教教义范围内进一步展开讨论的话题，话题的形式可以是问题或者指令。
                7.严格按json格式返回。{"view":<view>,"bible":<bible>,"explore":<explore>,"topic1":<topic1>,"topic2":<topic2>,"tag":<tag>,"summary":<summary>}
                8.对于跟信仰，圣经无关任何输入，如吃喝玩乐推荐、或者毫无意义的文本，只需要回复""。
                9.严格按照用户输入的语言返回。
                
                ###以下是view字段的详细要求：
                你要先识别用户是在问问题还是在记录。
如果用户是在问问题，他通常会用问句来做结尾，或者语义是一个具体的问题呈现。
接收到问题后，先回复一段共情用户
输入内容的开头，在基督教新教的框架内容上，去回答他的问题。回答问题时，请围绕【具体主题】进行回答，要求：
A. 标题加粗（用【】标注主题），首句先提炼核心结论；
​
B. 分点回答时使用 1. 2. 3. … 有序>列表，每点前用简短关键词加粗（如 核心优势：），内容简洁清晰；
​
C. 避免‘首先/然后’等过渡词，直接按逻辑顺序分点，每点控制在2-3句话，便于快速阅读，
D.在段与段之间要空一行。
字数在1000字以内。这一>类的内容，全部都归类到【信仰问答】的主题分类中。
如果问题超出了基督教新教的原则，或者有不确定之处，要写清楚这个观点来源，并提醒用户观点仅供参考。鼓励他可以把问题记录或收藏下来，日后在生活实践中，持续用这个恩
语app来记录，可能有新的亮光发现。
最后，推荐他一条与之相关的新教圣经中的经文作为结尾，标明经文的出处。
如果用户的问题涉及到政治，自杀，黄赌毒等敏感话题，温馨告知这类问题无法回答，可以帮他记录下来到一个新>的时间轴主题中，并给予一段积极正面的经文作为鼓励，让他知道无论经历多难的事情，上帝依然爱他，对他的生命有一个美好的计划。
如果用户是记录内容，不是问问题，无论是感恩小事，圣灵感动，亮光发现，讲道笔记等信息，
先用共情的语言回应用户的记录内容，再返回一段基督教新教的圣经中的相关经文进行鼓励。然后针对该经文予一段500字以内的内容拓展，可以说经文的经典人物背景，也可以讲这段经文的实际应用。如果用户是问圣经相关的问题，先回复一段共情用户输入内容的开头，再根据用户的问题进行回答，回答的内容要符合基督教新教的教义，或者基于圣经的常识性问题。如果用户的问题存在不同的观点，那就要列明这些都只是观点，仅供参考。回答的内容在800字以内。
圣经经文要高亮显示，要合理分段方便在手机查看，段落要分明。如有需要可以分点来回答，便于阅读者来阅读。
                
                
                !!!你必须根据用户使用的语言进行回复!!!
                ###以下是用户本次的输入内容：
                '''

msg_context = '''###以下是用户最近几次和AI对话的记录：
'''


msg_explore = '''你要在基督教正统教义范围内对下面输入进行以下反馈:
                1.view:用户查看的回应文本,必须是**Markdown 格式的字符串**（支持标题、列表、代码块等语法），圣经经文要高亮显示，要合理分段方便在手机查看，段落要分明。先回复一段共情用户输入内容的开头，再根据用户的问题进行回答，回答的内容要符合基督教新教的教义，或者基于圣经的常识性问题。如果用户的问题存在不同的观点，那就要列明这些都只是观点，仅供参考。可以根据回复的内容，给出一些符合圣经原则的实际应用的建议。
                2.bible:view字段回应包含的最主要的一节圣经经文，要包括经文全文和出处。例如“你们要将一切的忧虑卸给神，因为他顾念你们。”（彼前5:7）
                3.explore:给出1个和用户输入内容密切相关的，引导基督教新教教义范围内进一步展开讨论的话题，话题的形式可以是问题或者指令。
                4.严格按json格式返回。{"view":<view>,"bible":<bible>,"explore":<explore>}
                5.对于跟信仰，圣经无关任何输入，如吃喝玩乐推荐、或者毫无意义的文本，只需要回复""。
                6.严格按照用户输入的语言返回。
                
                !!!你必须根据用户使用的语言进行回复!!!
                 用户问题:
                '''

msg_pray = '''你要在基督教正统教义范围内对下面输入提供祷告和默想建议:
                1.view:针对用户的输入内容，提供与之相关的祷告和默想，以及返回一段符合基督教新教原则的实际应用建议，字数在500字以内。分为以下三部分:默想，祷告，实际应用。必须是**Markdown 格式的字符串**（支持标题、列表、代码块等语法），圣经经文要高亮，要合理分段方便在手机查看，段落要分明。
                2.bible:一句合适的圣经经文。要包括经文全文和出处。例如“你们要将一切的忧虑卸给神，因为他顾念你们。”（彼前5:7）
                3.explore:字符串数组形式给出2个和用户输入内容密切相关的，引导基督教新教教义范围内进一步展开讨论的话题，话题的形式可以是问题或者指令。
                4.严格按json格式返回。{"view":<view>,"bible":<bible>,"explore":[explore1,explore2]}
                5.对于跟信仰，圣经无关任何输入，如吃喝玩乐推荐、或者毫无意义的文本，只需要回复""。
                6.严格按照用户输入的语言返回。
                
                !!!你必须根据用户使用的语言进行回复!!!
                以下是用户的输入内容：
                '''
msg_error = '''我很乐意帮你做大小事情的记录，都会成为你看见上帝恩典的点点滴滴。但这个问题我暂时没有具体的推荐，你有此刻想记录的心情或亮光想记录吗？
'''

# 黄色：信靠，盼望，刚强，光明 #FFFBE8
# 红色：慈爱，喜乐 #FFEEEB
# 蓝色：安慰，永恒 #EDF8FF
# 绿色：平安，恩典 #E8FFFF

color_map = {"#FFFBE8": ("信靠", "盼望", "刚强", "光明"),
             "#FFEEEB": ("慈爱", "喜乐"),
             "#EDF8FF": ("安慰", "永恒"),
             "#E8FFFF": ("平安", "恩典")}


class CozeService:
    bot_id = "7481241756508504091"
    executor = ThreadPoolExecutor(3)

    @staticmethod
    def chat_with_coze_async(user_id, msg_id):
        '''
        :param user_id:
        :param msg_id: 1 用户正常记录；其他 用户探索
        :return:
        '''
        try:
            logger.info(f"chat_with_coze_async: {user_id, msg_id}")
            CozeService.executor.submit(CozeService.chat_with_coze, user_id, msg_id)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def is_explore_msg(message):
        return len(message.context_id) > 5

    @staticmethod
    def chat_with_coze(user_id, msg_id):
        session = None
        from models.message import Message
        try:
            session = DBSession()
            message = session.query(Message).filter_by(id=msg_id, status=0).first()
        except exc.OperationalError as e:
            session.rollback()
            logger.exception(e)
            engine.dispose()
            session = DBSession()
            message = session.query(Message).filter_by(id=msg_id, status=0).first()
        except Exception as e:
            logger.exception(e)
            return

        from services.message_service import MessageService
        if message.action == MessageService.action_bible_pic:
            message.status = 2
            message.feedback_text = "(实现中)将会为你生成经文图片"
            session.commit()
            return

        try:
            custom_prompt = message.feedback_text
            message.status = 1
            session.commit()
            session_lst = []
            is_explore = CozeService.is_explore_msg(message)
            from models.session import Session
            if is_explore:
                # 用户探索类型
                if message.action == MessageService.action_daily_pray:
                    context_msg = session.query(Message).filter_by(public_id=message.context_id).first()
                    if context_msg:
                        context_content = context_msg.content
                    else:
                        context_content = message.content
                    ask_msg = (custom_prompt + context_content) if custom_prompt else msg_pray + context_content
                else:
                    ask_msg = (custom_prompt + message.content) if custom_prompt else msg_explore + message.content
                # rsp_msg = message
            else:
                # rsp_msg = Message(0, user_id, "", context_id, 1)
                # session.add(rsp_msg)
                # session.commit()
                session_lst = session.query(Session).filter_by(owner_id=user_id).order_by(
                    desc(Session.id)).with_entities(Session.id, Session.session_name).limit(100).all()
                names = "["
                for session_id, session_name in session_lst:
                    names += f"\"{session_name}\","
                names += "]"

                ask_msg = custom_prompt.replace("${event}", names) if custom_prompt else msg_feedback.replace(
                    "${event}", names)
                ask_msg += message.content

                messages = Message.query.filter_by(owner_id=2).filter(Message.id < 1117).order_by(desc(Message.id)).limit(5)
                if messages:
                    desc = ""
                    for m in messages:
                        desc +=f"id:{m.id},用户输入:{m.content},AI回应:{m.feedback_text}"
                    ask_msg+=msg_context+desc

            ask_msg = msg_json+ask_msg
            response = CozeService._chat_with_coze(session, message, user_id, ask_msg)
            if response:
                logger.warning(f"GOT: {response}")
                try:
                    result = json.loads(response)
                    bible, view = result.get('bible'), result.get('view')
                    if view:
                        message.feedback_text = view
                    else:
                        message.feedback_text = msg_error + ",原始回复:" + response
                    if not is_explore:
                        summary = result.get("summary")
                        if summary:
                            message.summary = summary
                        tag = result.get("tag")
                        if tag:
                            for k, v in color_map.items():
                                if tag in v:
                                    result["color_tag"] = k
                                    break
                    if not is_explore and not message.session_id:
                        topic = result.get("topic1")
                        if not topic:
                            topic = result.get("topic2")
                        if topic:
                            result["topic"] = topic
                            for session_id, session_name in session_lst:
                                if topic == session_name:
                                    message.session_id = session_id
                                    session.query(Session).filter_by(id=session_id).update({
                                        "updated_at": func.now()
                                    })
                                    session.commit()
                                    break
                            if not message.session_id and topic:
                                new_session = Session(topic, user_id, 0)
                                session.add(new_session)
                                session.commit()
                                message.session_id = new_session.id
                    response = json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    message.feedback_text = msg_error + ",原始回复:" + response
                    logger.exception(e)
                message.feedback = response
                message.status = 2
                session.commit()
        except Exception as e:
            logger.exception(e)
            if message and message.status != 2:
                message.status = 2
                message.feedback_text = "AI回复异常，请重试"
                session.commit()

        # finally:
        #     if session:
        #         session.close()  # 重要！清理会话

    @staticmethod
    def create_conversations():
        conversation = coze.conversations.create()
        return conversation.id

    @staticmethod
    def _extract_content(text, s):
        import re
        s1, e1, s2, e2 = s
        bible, detail = "", ""

        if not s1:
            match = re.search(r"(\"view\"\s*:\s*\")", text)
            if match:
                s[0] = s1 = match.end()

        if not s2:
            match = re.search(r"(\"bible\"\s*:\s*\")", text)
            if match:
                s[1] = e1 = match.start()
                s[2] = s2 = match.end()

        if not e2:
            match = re.search(r"(\"explore\"\s*:\s*)", text)
            if match:
                s[3] = e2 = match.start()
        if s1:
            detail = text[s1:e1 if e1 > 0 else -1]
        if s2:
            bible = text[s2:e2 if e2 > 0 else -1]
        return bible, detail

    @staticmethod
    def _chat_with_coze(session, ori_msg, user_id, msg):
        all_content = ""
        pos = [0, 0, 0, 0]
        logger.info(f"_chat_with_coze: {user_id, msg}")
        # is_explore = CozeService.is_explore_msg(ori_msg)
        for event in coze.chat.stream(
                bot_id=CozeService.bot_id,
                user_id=str(user_id),
                additional_messages=[Message.build_user_question_text(msg)],
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                message = event.message
                all_content += message.content
                if 1:
                    if pos[3] <= 0:
                        bible, detail = CozeService._extract_content(all_content, pos)
                        ori_msg.feedback_text = detail.replace(r'\n', '\n')
                # else:
                #     ori_msg.feedback_text = all_content
                # logger.info(f"CONVERSATION_MESSAGE_DELTA: {ori_msg.feedback}")
                ori_msg.status = 1
                session.commit()
            elif event.event == ChatEventType.CONVERSATION_MESSAGE_COMPLETED and event.message.type == MessageType.ANSWER:
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
