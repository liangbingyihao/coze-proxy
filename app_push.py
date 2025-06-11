import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate(r"D:\work\testim-ae3cf-firebase-adminsdk-fbsvc-0e89da8c56.json")
firebase_admin.initialize_app(cred)


def send_to_device(device_token, title, body, data=None):
    """
    向单个设备发送推送通知

    参数:
        device_token (str): 目标设备的 FCM 注册令牌
        title (str): 通知标题
        body (str): 通知正文
        data (dict): 可选的自定义数据键值对
    """
    # 创建消息
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=device_token,
        data=data,  # 可选的自定义数据字典
    )

    try:
        # 发送消息
        response = messaging.send(message)
        print('成功发送消息:', response)
        return True
    except Exception as e:
        print('发送消息失败:', str(e))
        return False


# 使用示例
device_token = "deL9dDVVTwSOAUm7-gy3TA:APA91bEWd-C-i_ufIOQ437I9-cRBajwZgiygzDEEz_AwO_BV96zoGeybiMPW0ZOUFOjn6b8hZw8ajvXg2DVgKff7hLvPSGZAhXFl9CE4epucNWh5RCwFNcs"  # 替换为实际的设备令牌
send_to_device(
    device_token,
    title="新消息通知",
    body="您有一条新的消息，请查收！",
    data={"message_id": "12345", "type": "new_message"}
)