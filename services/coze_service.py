import os

coze_api_token = os.getenv("COZE_API_TOKEN")

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType, COZE_CN_BASE_URL,COZE_COM_BASE_URL  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)

# Create a bot instance in Coze, copy the last number from the web link as the bot's ID.
bot_id = "7481241756508504091"
# The user id identifies the identity of a user. Developers can use a custom business ID
# or a random string.
user_id = "1234567"
user_id = "12345678"

# Call the coze.chat.stream method to create a chat. The create method is a streaming
# chat and will return a Chat Iterator. Developers should iterate the iterator to get
# chat event and handle them.
all_content = ""
for event in coze.chat.stream(
    bot_id=bot_id, user_id=user_id, additional_messages=[Message.build_user_question_text("返回今天所有祷告内容")]
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        message = event.message
        all_content+=message.content
        # print(f"role={message.role}, content={message.content}")
print(all_content)