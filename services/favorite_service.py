import json
import logging

from flask_sqlalchemy import Pagination
from sqlalchemy import desc

from models.favorites import Favorites
from models.message import Message
from extensions import db
from models.session import Session
from services.coze_service import CozeService
from services.message_service import MessageService
from services.session_service import SessionService
from utils.exceptions import AuthError


class FavoriteService:
    content_type_user = 1
    content_type_ai = 2

    @staticmethod
    def new_favorite(owner_id, message_id, content_type):
        '''
        :param owner_id:
        :param message_id:
        :param content_type:
        :return:
        '''
        # session_owner, session_name, conversation_id = MessageService.check_permission(session_id, owner_id)
        # logging.debug(f"session:{session_owner, session_name}")
        message = Message.query.filter_by(public_id=message_id, owner_id=owner_id).one()
        if message:
            if content_type == FavoriteService.content_type_ai:
                content = message.feedback_text
            else:
                content_type = FavoriteService.content_type_user
                content = message.content

            favorite = Favorites(owner_id, message_id, content_type, content)
            db.session.add(favorite)
            db.session.commit()
            return True

    @staticmethod
    def delete_favorite(owner_id, message_id, content_type):
        """
        删除指定用户的收藏记录
        :param owner_id: 用户ID（用于权限验证）
        :param message_id: 要删除的收藏ID
        :return: 成功返回True，失败返回False
        """
        try:
            # 查询并验证收藏记录归属
            favorite = Favorites.query.filter_by(message_id=message_id, owner_id=owner_id, content_type=content_type).first()

            if not favorite:
                logging.warning(f"Favorite not found or permission denied. User: {owner_id}, Favorite: {message_id,content_type}")
                return False

            # 执行删除
            db.session.delete(favorite)
            db.session.commit()
            logging.info(f"Favorite deleted. ID: {favorite.id}")
            return True

        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to delete favorite {message_id}: {str(e)}", exc_info=True)
            return False

    # @staticmethod
    # def get_session_by_id(session_id):
    #     return Session.query.get(session_id)


    @staticmethod
    def get_favorite_by_owner(owner_id, page, limit):
        items = Favorites.query.filter_by(owner_id=owner_id).order_by(desc(Favorites.id)) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()
        return Pagination(query=None, page=page, per_page=limit, items=items, total=None)
        # return Favorites.query.filter_by(owner_id=owner_id).order_by(desc(Favorites.id)).paginate(page=page, per_page=limit, error_out=False)


    @staticmethod
    def get_message(owner_id, msg_id):
        if msg_id == "welcome":
            return MessageService.welcome_msg
        else:
            message = Message.query.filter_by(public_id=msg_id, owner_id=owner_id).one()
            try:
                feedback = json.loads(message.feedback)
                explore = feedback.get("explore")
                if explore:
                    funcs = []
                    if isinstance(explore, list):
                        for i in explore:
                            funcs.append([i, MessageService.action_daily_talk])
                    else:
                        funcs.append([explore, MessageService.action_daily_talk])
                    if feedback.get("bible"):
                        funcs.append(["请把上面的经文内容做成一个可以分享的经文图", MessageService.action_bible_pic])
                    if message.action != MessageService.action_daily_pray:
                        funcs.append(["关于以上内容的祷告和默想建议", MessageService.action_daily_pray])
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
                return False
        if session_name:
            session = SessionService.new_session(session_name, owner_id, 0)
            session_id = session.id
        message = Message.query.filter_by(public_id=msg_id, owner_id=owner_id).first()
        if message:
            if summary:
                message.summary = summary
            if session_id:
                message.session_id = session_id
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
            message.session_id = session_id
            db.session.commit()
            return True
