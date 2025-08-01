import json
import logging

from sqlalchemy import desc, or_, and_

from models.message import Message
from extensions import db
from models.session import Session
from services.coze_service import CozeService
from services.session_service import SessionService
from utils.exceptions import AuthError


class MessageService:
    action_daily_talk = 0
    action_bible_pic = 1
    action_daily_gw = 2
    action_direct_msg = 3
    action_daily_pray = 4
    action_input_prompt = 5

    content_type_user = 1
    content_type_ai = 2
    explore = [["我想看今天的【每日恩语】", action_daily_gw],
               ["我想把上面的经文做成“经文图”，分享给身边的弟兄姊妹，一起思想神的话语！", action_bible_pic],
               ["我记录当下心情或事件后，你会如何帮我整理", action_direct_msg, "对应的答案"]]
    welcome_msg = {
        "action": 0,
        "content": "",
        "context_id": "0",
        "created_at": "2025-05-28T03:40:49",
        "feedback": {
            "bible": "我的恩典够你用，因为我的能力是在人的软弱上显得完全。（哥林多后书 12:9）",
            "function": [
                [
                    "我想看今天的【每日恩语】",
                    action_daily_gw
                ],
                [
                    "我想把上面的经文做成“经文图”，分享给身边的弟兄姊妹，一起思想神的话语！",
                    action_bible_pic
                ],
                [
                    "我记录当下心情或事件后，你会如何帮我整理",
                    3, '''
# 🌈 信心鼓励

假设你输入心情：  
**"在最近的生活变动和迷茫中，虽然暂时看不到方向，甚至对神的安排产生疑问，但最终选择信靠祂的应许——祂深知你的需要，且预备的恩典远超你的期待。"**

---

## 📝 已记录到【信心功课】  
（后续可以在时间轴中查看）  

---

## ✨ 今日经文鼓励  
**"神为爱他的人所预备的，是眼睛未曾看见，耳朵未曾听见，人心也未曾想到的。"**  
（哥林多前书 2:9）

---

## 🌱 信心操练指南  

信心的功课不容易，神的预备是每日的功课，**不需看清全程，只需信靠每一步**。  

我们可以通过以下几点进行操练：  

1. **🙏 交托祷告**  
   - 写下困惑，向神坦白：  
     *"我相信你的预备超乎所想，但求你给我信心。"*  

2. **⚔️ 对抗埋怨**  
   - 当怀疑时，默想这节经文并回顾神过去的信实。  

3. **⏳ 积极等候**  
   - 专注当下责任（如工作、服侍），像约瑟在监狱中仍尽忠。  

4. **🌍 开阔信心**  
   - 设想神可能带领的多种方式，祷告求祂显明，不局限自己的期待。  

5. **🤝 寻求支持**  
   - 与属灵同伴分享经文，请他们为你守望。  
 '''
                ]
            ],
        },
        "feedback_text": '''✨嗨，你好🙌欢迎来到恩语~！
我可以为你记录你的每一件感恩小事💝、圣灵感动🔥、真实感受，甚至讲道亮光🌟哦，
帮助你在信仰路上，不断看到上帝的恩典🌈！
📝文字或🎤语音转文字，就能快速记录，我们会帮你整理⏳~
每天的记录都是我们跟神互动的印记💌，
坚持记录，你很快会发现，上帝如何奇妙地与我们同行👣哦！
快来开始记录吧~🎉  
根据你的记录，我们会返回给你一段圣经的话语，看看是否能给你带来新的发现或鼓励哦~
哥林多后书12：9说：“我的恩典够你用，因为我的能力是在人的软弱上显得完全！”
''',
        "id": "welcome",
        "session_id": 0,
        "status": 2,
        "summary": ""
    }

    @staticmethod
    def init_welcome_msg():
        messages = Message.query.filter_by(owner_id=2).filter(Message.id < 1117).order_by(desc(Message.id)).limit(5)
        for m in messages:
            print(m)

    @staticmethod
    def check_permission(session_id, owner_id):
        session = Session.query.filter_by(id=session_id).with_entities(Session.owner_id, Session.session_name,
                                                                       Session.conversation_id).one()
        # session_owner,session_name = session[0],session[1]
        if session[0] != owner_id:
            raise AuthError('session no permission', 404)
        return session

    @staticmethod
    def renew(owner_id, msg_id, prompt):
        '''
        :param msg_id:
        :param prompt:
        :param owner_id:
        :return:
        '''
        # session_owner, session_name, conversation_id = MessageService.check_permission(session_id, owner_id)
        # logging.debug(f"session:{session_owner, session_name}")
        message = Message.query.filter_by(public_id=msg_id, owner_id=owner_id).one()
        if message:
            message.status = 0
            message.feedback_text = prompt or ""
            db.session.commit()
            CozeService.chat_with_coze_async(owner_id, message.id)
            return message.public_id

    @staticmethod
    def del_msg(owner_id, msg_id, content_type):
        '''
        :param msg_id:
        :param content_type:
        :param owner_id:
        :return:
        '''
        message = Message.query.filter_by(public_id=msg_id, owner_id=owner_id).one()
        if message:
            if content_type == MessageService.content_type_user:
                SessionService.reset_updated_at(message.session_id)
                message.content = ""
                message.session_id = -1
            elif content_type == MessageService.content_type_ai:
                message.feedback_text = ""
            else:
                return None

            if not message.content and not message.feedback_text:
                message.status = 3
            db.session.commit()
            return message.public_id

    @staticmethod
    def new_message(owner_id, content, context_id, action, prompt):
        '''
        :param action:
        :param prompt:
        :param context_id:用户探索的原信息id
        :param owner_id:
        :param content:
        :return:
        '''
        # session_owner, session_name, conversation_id = MessageService.check_permission(session_id, owner_id)
        # logging.debug(f"session:{session_owner, session_name}")
        message = None
        if content:
            if prompt:
                logging.warning(f"prompt:{owner_id, content, action, prompt}")
            message = Message(0, owner_id, content, context_id, action=action)
            message.feedback_text = prompt or ""
            db.session.add(message)
            db.session.commit()
            logging.warning(f"message.id:{message.id}")

        CozeService.chat_with_coze_async(owner_id, message.id)

        return message.public_id

    # @staticmethod
    # def get_session_by_id(session_id):
    #     return Session.query.get(session_id)

    @staticmethod
    def filter_message(owner_id, session_id, session_type, search, page, limit):
        '''
        :param owner_id:
        :param session_id:
        :param session_type: #"topic", "question"
        :param search:
        :param page:
        :param limit:
        :return:
        '''
        conditions = [Message.owner_id == owner_id]
        if session_id and isinstance(session_id, int):
            conditions.append(Message.session_id == session_id)
        elif session_type:
            if session_type == "topic":
                conditions.append(Message.session_id > 0)
            elif session_type == "question":
                session = Session.query.filter_by(owner_id=owner_id, session_name="信仰问答").first()
                if session:
                    conditions.append(Message.session_id == session.id)
                else:
                    return []

        if search and search.strip():
            if session_type == "topic":
                conditions.append(Message.content.contains(search))
            else:
                conditions.append(or_(
                    Message.content.contains(search),
                    Message.feedback.contains(search)
                ))
        query = Message.query.filter(
            and_(*conditions)
        )
        return query.order_by(desc(Message.id)) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()

    @staticmethod
    def search_message(owner_id, source, search, page, limit):
        # 1:会话，2：时间轴，3：信仰问答，4：收藏
        conditions = [Message.owner_id == owner_id]
        if source == 2:
            conditions.append(Message.session_id > 0)
        elif source == 3:
            session = Session.query.filter_by(owner_id=owner_id, session_name="信仰问答").first()
            if session:
                conditions.append(Message.session_id == session.id)
            else:
                return []
        elif source == 4:
            pass
        conditions.append(or_(
            Message.content.contains(search),
            Message.feedback.contains(search)
        ))
        query = Message.query.filter(
            and_(*conditions)
        )

        return query.order_by(desc(Message.id)) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()
        # messages = query.paginate(page=page, per_page=limit, error_out=False)

    @staticmethod
    def get_message(owner_id, msg_id):
        if msg_id == "welcome":
            return MessageService.welcome_msg
        else:
            message = Message.query.filter_by(public_id=msg_id, owner_id=owner_id).one()
            try:
                feedback = json.loads(message.feedback)
                funcs = []
                explore = feedback.get("explore")
                if explore:
                    if isinstance(explore, list):
                        for i in explore:
                            funcs.append([i, MessageService.action_daily_talk])
                    else:
                        funcs.append([explore, MessageService.action_daily_talk])
                    # if feedback.get("bible"):
                    #     funcs.append(["请把上面的经文内容做成一个可以分享的经文图", MessageService.action_bible_pic])
                    # if message.action != MessageService.action_daily_pray:
                    #     funcs.append(["关于以上内容的祷告和默想建议", MessageService.action_daily_pray])

                explore = feedback.get("prompt")
                if explore:
                    if isinstance(explore, list):
                        for i in explore:
                            funcs.append([i, MessageService.action_input_prompt])
                    else:
                        funcs.append([explore, MessageService.action_input_prompt])

                if funcs:
                    feedback["function"] = funcs
                message.feedback = feedback

                if not message.summary:
                    message.summary = feedback.get("summary")
            except Exception as e:
                pass
            return message

    @staticmethod
    def filter_msg_by_context_id(owner_id, session_id, context_id):
        session = MessageService.check_permission(session_id, owner_id)
        return Message.query.filter_by(context_id=context_id)

    @staticmethod
    def set_summary(owner_id, msg_id, summary, session_id, session_name):
        if session_id and session_id > 0:
            session = Session.query.filter_by(owner_id=owner_id, id=session_id).one()
            if not session:
                raise Exception("no session")
        if session_name:
            session = SessionService.new_session(session_name, owner_id, 0)
            session_id = session.id
        message = Message.query.filter_by(public_id=msg_id, owner_id=owner_id).first()
        if message:
            if summary:
                message.summary = summary
            if session_id:
                last_session_id = message.session_id
                message.session_id = session_id
                SessionService.reset_updated_at(last_session_id)
            db.session.commit()
            return message.session_id

    @staticmethod
    def set_session_id(owner_id, msg_id, session_id):
        if session_id > 0:
            cnt_session = Session.query.filter_by(owner_id=owner_id, session_id=session_id).count()
            if cnt_session <= 0:
                return False
        message = Message.query.filter_by(public_id=msg_id, owner_id=owner_id).one()
        if message:
            last_session_id = message.session_id
            message.session_id = session_id
            db.session.commit()
            SessionService.reset_updated_at(last_session_id)
            return True
