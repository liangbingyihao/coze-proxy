import json
import logging
import time

from models.message import Message
from extensions import db
from models.session import Session
from services.coze_service import CozeService
from utils.exceptions import AuthError


class MessageService:
    action_bible_pic=2
    action_daily_gw=1
    action_direct_msg=3
    action_daily_ai=0
    explore = [["我想看包含了今天的经文推荐，实际应用，以及今天大事的“每日恩语”", action_daily_gw],
               ["我想看今天的鼓励经文推荐图", action_bible_pic],
               ["直接客户端回答的问题", action_direct_msg, "对应的答案"]]

    @staticmethod
    def init_welcome_msg():
        message = Message.query.filter_by(owner_id=0).first()
        is_new=False
        if not message:
            message = Message(
                session_id=0, owner_id=0, content="", context_id=0, status=0, action=0
            )
            is_new = True
        message.feedback_text = '''✨嗨，你好🙌欢迎来到恩语~！
    我可以为你记录你的每一件感恩小事💝、圣灵感动🔥、真实感受，甚至讲道亮光🌟哦，
    帮助你在信仰路上，不断看到上帝的恩典🌈！
    📝文字或🎤语音转文字，就能快速记录，我们会帮你整理⏳~
    每天的记录都是我们跟神互动的印记💌，
    坚持记录，你很快会发现，上帝如何奇妙地与我们同行👣哦！
    快来开始记录吧~🎉  
    '''
        message.feedback = json.dumps(
            {"function": [["我想看包含了今天的经文推荐，实际应用，以及今天大事的“每日恩语”", 1],
                         ["我想看今天的鼓励经文推荐图", 2],
                         ["我记录当下心情或事件后，你会如何帮我整理", 3, '''假设你语音转文字输入心情：在最近的生活变动和迷茫中，虽然暂时看不到方向，甚至对神的安排产生疑问，但最终选择信靠祂的应许——祂深知你的需要，且预备的恩典远超你的期待。
    我们已经把你的内容记录到【信心功课】，希望这段经文可以鼓励到你：
    “神为爱他的人所预备的，是眼睛未曾看见，耳朵未曾听见，人心也未曾想到的。”（哥林多前书2:9）
    信心的功课不容易，神的预备是每日的功课，不需看清全程，只需信靠每一步。
    我们可以通过以下几点进行操练：
     1交托祷告 ：写下困惑，向神坦白：“我相信你的预备超乎所想，但求你给我信心。
     2对抗埋怨 ：当怀疑时，默想这节经文并回顾神过去的信实。
     3积极等候 ：专注当下责任（如工作、服侍），像约瑟在监狱中仍尽忠。
     4开阔信心 ：设想神可能带领的多种方式，祷告求祂显明，不局限自己的期待。
     5寻求支持 ：与属灵同伴分享经文，请他们为你守望。''']]}, ensure_ascii=False)
        if is_new:
            db.session.add(message)
        db.session.commit()
        print("Initialized the database with welcome msg.")

    @staticmethod
    def check_permission(session_id, owner_id):
        session = Session.query.filter_by(id=session_id).with_entities(Session.owner_id, Session.session_name,
                                                                       Session.conversation_id).one()
        # session_owner,session_name = session[0],session[1]
        if session[0] != owner_id:
            raise AuthError('session no permission', 404)
        return session

    @staticmethod
    def new_message(owner_id, content, context_id):
        '''
        :param context_id:用户探索的原信息id
        :param owner_id:
        :param content:
        :return:
        '''
        # session_owner, session_name, conversation_id = MessageService.check_permission(session_id, owner_id)
        # logging.debug(f"session:{session_owner, session_name}")
        message = None
        if content:
            message = Message(0, owner_id, content, context_id)
            db.session.add(message)
            db.session.commit()
            logging.warning(f"message.id:{message.id}")

        CozeService.chat_with_coze_async(owner_id, message.id)

        return message.public_id

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
    def get_message(owner_id, msg_id):
        if msg_id == "welcome":
            return Message.query.filter_by(owner_id=0).one()
        else:
            message = Message.query.filter_by(public_id=msg_id, owner_id=owner_id).one()
            try:
                feedback = json.loads(message.feedback)
                feedback["function"]=[[feedback.get("explore"),MessageService.action_daily_ai],
                                      ["请把上面的经文内容做成一个可以分享的经文图",MessageService.action_daily_gw],
                                      ["关于以上内容的祷告和默想建议",MessageService.action_daily_ai]]
                message.feedback = feedback
            except Exception as e:
                pass
            return message

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
