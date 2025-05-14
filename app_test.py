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
        "guest": "guestest",
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
        # "session_name": "session_name1",
        "robt_id": "0"
    }


    response = requests.post("http://8.217.172.116:5000/api/session", headers=headers, json=data)
    print(response.text)

def my_session(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "page":1,
        "limit":50
    }


    response = requests.get("http://8.217.172.116:5000/api/session", headers=headers,params=data)
    sessions = response.json().get("data")
    for s in sessions.get("items"):
        print(s)

def add_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "text": "如何以祷告引导孩子改变？",
        "context_id": "2",
    }
    data = {
        "text": "很担心这次考试",
    }
    # data = {
    #     "text":1
    # }

    response = requests.post("http://8.217.172.116:5000/api/message", headers=headers,json=data)
    print(response.text)

def my_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_id":2,
        "context_id":21,
        # "page":1,
        # "limit":1
    }
    response = requests.get("http://8.217.172.116:5000/api/message", headers=headers,params=data)
    print(response.json())

def get_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_id":2,
        "context_id":21,
        # "page":1,
        # "limit":1
    }
    response = requests.get("http://8.217.172.116:5000/api/message/9", headers=headers)
    r = response.json()
    print(r)
    return r


def _extract_feedback(content,s):
    s1,s2,s3 = s
    if not s1:
        s[0] = s1 = content.find("\"bible\":")
    if s1 and not s2:
        s[1] = s2 = content.find("\", \"feed")
    if s2 and not s3:
        s[2] = s3 = content.find("\", \"exp")
    bible,feedbcak = content[s1+8:s2+1 if s2>0 else -1],content[s2+14:s3+1 if s3>0 else -1]
    return bible,feedbcak

if __name__ == '__main__':
    # register()
    token = login("user2")
    r = get_message(token)
    feedback = r.get("data").get("feedback")
    pos=[0,0,0]
    _extract_feedback(feedback,pos)
    print(pos)