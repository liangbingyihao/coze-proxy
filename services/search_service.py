from sqlalchemy import desc, or_, and_
from sqlalchemy.orm import load_only

from models.message import Message
from models.session import Session
from services.favorite_service import FavoriteService


class SearchService:

    @staticmethod
    def _extract_snippet(text, keyword, context_len=50):
        pos = text.find(keyword)
        if pos == -1:
            return None
        start = max(0, pos - context_len)
        end = min(len(text), pos + len(keyword) + context_len)
        return text[start:end]

    @staticmethod
    def handle_snippet(messages, search):
        for msg in messages:
            msg["content"] = SearchService._extract_snippet(msg["content"], search)
        return messages

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
        if not search or not search.strip():
            return []

        if session_type == "favorite":
            return SearchService.handle_snippet(FavoriteService.get_favorite_by_owner(owner_id, page=page,
                                                                                      limit=limit, search=search),
                                                search)
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

        message_id = Message.public_id.label('message_id')
        if session_type == "topic":
            conditions.append(Message.content.contains(search))
            query = (Message.query.options(load_only(Message.public_id, Message.content, Message.created_at))
            .add_columns(
                message_id,
                Message.content,
                Message.created_at
            )
            .filter(
                and_(*conditions)
            ))
        else:
            conditions.append(or_(
                Message.content.contains(search),
                Message.feedback_text.contains(search)
            ))
            query = (Message.query.options(
                load_only(Message.public_id, Message.content, Message.feedback_text, Message.created_at))
            .add_columns(
                message_id,
                Message.content,
                Message.feedback_text,
                Message.created_at
            )
            .filter(
                and_(*conditions)
            ))
        return query.order_by(desc(Message.id)) \
            .offset((page - 1) * limit) \
            .limit(limit) \
            .all()
