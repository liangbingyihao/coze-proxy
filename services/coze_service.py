import logging
import os


coze_api_token = os.getenv("COZE_API_TOKEN")

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType, COZE_CN_BASE_URL,COZE_COM_BASE_URL  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.

class CozeService:
    bot_id = "7481241756508504091"

    @staticmethod
    def chat_with_coze(user_id,context_id):
        from models.message import Message
        from models.user import User
        message = Message.query.filter_by(id=context_id,status=0).with_entities(Message.content).one()
        user = User.query.filter_by(id=user_id).with_entities(User.username).one()
        logging.warning(f"GOT: {user_id,context_id,message,user}")

    @staticmethod
    def _chat_with_coze(cls,user_id,msg):
        all_content = ""
        for event in coze.chat.stream(
            bot_id=cls.bot_id, user_id=user_id, additional_messages=[Message.build_user_question_text(msg)]
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                message = event.message
                all_content+=message.content
                # print(f"role={message.role}, content={message.content}")
        return all_content