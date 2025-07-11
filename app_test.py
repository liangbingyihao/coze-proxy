import json
from json import JSONDecodeError

import requests


def register():
    url = "http://8.217.172.116:5000/api/auth/register"
    data = {
        "username": "user2",
        "email": "user2@163.com",
        "password": "123456"
    }

    response = requests.post(url, json=data)
    print(response.text)


def login(user_name):
    url = "http://8.217.172.116:5000/api/auth/login"
    data = {
        "guest": "81863ba6-abf8-340f-892a-683e6896a23f",
        "password": "123456"
    }

    response = requests.post(url, json=data)
    print(response.text)
    token = response.json().get("data").get("access_token")
    return token


def new_session(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_name": "session_name2",
        "robot_id": "1"
    }

    response = requests.post("http://8.217.172.116:5000/api/session", headers=headers, json=data)
    print(response.text)


def my_session(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "page": 1,
        "limit": 50
    }

    response = requests.get("http://8.217.172.116:5000/api/session", headers=headers, params=data)
    sessions = response.json().get("data")
    for s in sessions.get("items"):
        print(s)


def del_session(token, session_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_id": session_id
    }

    response = requests.post("http://8.217.172.116:5000/api/session/del", headers=headers, json=data)
    sessions = response.json()
    print(sessions)


def get_conf(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "page": 1,
        "limit": 50
    }

    response = requests.get("http://8.217.172.116:5000/api/system/conf", headers=headers, params=data)
    data = response.json().get("data")
    print(data)


def add_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "text": "今天和邻居聊了一个上午，但还没有解开大家的心结",
        "context_id": "2",
        "prompt": "test"
    }
    #     data = {
    #         "text": '''✨嗨，你好🙌欢迎来到恩语~！
    # 我可以为你记录你的每一件感恩小事💝、圣灵感动🔥、真实感受，甚至讲道亮光🌟哦，
    # 帮助你在信仰路上，不断看到上帝的恩典🌈！
    # 📝文字或🎤语音转文字，就能快速记录，我们会帮你整理⏳~
    # 每天的记录都是我们跟神互动的印记💌，
    # 坚持记录，你很快会发现，上帝如何奇妙地与我们同行👣哦！
    # 快来开始记录吧~🎉
    # ''',
    #     }
    # data = {
    #     "text":1
    # }

    response = requests.post("http://8.217.172.116:5000/api/message", headers=headers, json=data)
    print(response.text)


def my_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "search": "避难所",
        "session_type":"feed"
        # "source":3
        # "context_id":21,
        # "page":1,
        # "limit":1
    }
    response = requests.get("http://8.217.172.116:5000/api/message/filter", headers=headers, params=data)
    print(response.text)
    items = response.json().get("data").get("items")
    for i in items:
        print(i)

def renew_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "message_id":"dca17748-42ee-4a3b-9162-953219133c34"
        # "source":3
        # "context_id":21,
        # "page":1,
        # "limit":1
    }
    response = requests.post("http://8.217.172.116:5000/api/message/renew", headers=headers, json=data)
    print(response.text)

def get_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_id": 2,
        "context_id": 21,
        # "page":1,
        # "limit":1
    }
    msg_id = "dd147a2d-cb8d-45ba-8042-06ef28a7a6b8"
    msg_id = "welcome"
    response = requests.get(f"http://8.217.172.116:5000/api/message/{msg_id}", headers=headers)
    r = response.json()
    print(json.dumps(r.get("data"), indent=4, ensure_ascii=False))
    return r


def update_summary(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "summary": "心结难解"
    }
    response = requests.post("http://8.217.172.116:5000/api/message/c198b09d-2ac7-4f6a-8f2b-9511d78c7049",
                             headers=headers, json=data)
    r = response.json()
    print(r)
    return r


def _extract_content(content, s):
    print(content)
    s1, s2, s3 = s
    if not s1:
        s[0] = s1 = content.find("\"bible\":")
    if s1 and not s2:
        s[1] = s2 = content.find("\"feed")
    if s2 and not s3:
        s[2] = s3 = content.find("\"exp")
    bible, detail = content[s1 + 8:s2 if s2 > 0 else -1], content[s2 + 11:s3 if s3 > 0 else -1]
    return bible, detail


def extract_test(text, s):
    import re
    s1, e1, s2, e2 = s
    bible, detail = "", ""

    if not s1:
        match = re.search(r"(\"bible\"\s*:\s*)", text)
        if match:
            s[0] = s1 = match.end()

    if not s2:
        match = re.search(r"(\"feedback\"\s*:\s*)", text)
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
        detail = text[s2:e2 if e2 > 0 else -1]
    return bible, detail


def add_favorite(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "message_id": "f6ed0f6e-3026-4729-afc8-cfd016f0fd34",
        "content_type": 2
    }
    response = requests.post("http://8.217.172.116:5000/api/favorite", headers=headers, json=data)
    print(response.text)


def toggle_favorite(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "message_id": "f6ed0f6e-3026-4729-afc8-cfd016f0fd34",
        "content_type": 2
    }
    response = requests.post("http://8.217.172.116:5000/api/favorite/toggle", headers=headers, json=data)
    print(response.text)


def my_favorite(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        # "session_id": 12,
        # "context_id":21,
        "page": 1,
        "limit": 2,
        "search":"英文"
    }
    response = requests.get("http://8.217.172.116:5000/api/favorite", headers=headers, params=data)
    print(response.json())


if __name__ == '__main__':
    token = login("user2")
    # # get_conf(token)
    # my_favorite(token)
    renew_message(token)
    # r = my_session(token)
    # print(extract_test(r.get("data").get("feedback")[0:200],[0,0,0,0]))
