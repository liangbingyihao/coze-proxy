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
        "username": user_name,
        "password": "123456"
    }

    response = requests.post(url, json=data)
    token = response.json().get("data").get("access_token")
    print(response.text,token)
    return token

def new_session(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_name": "session_name1",
        "robt_id": "0"
    }


    response = requests.post("http://8.217.172.116:5000/api/session/add", headers=headers, json=data)
    print(response.json())

def my_session(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "session_name": "session_name1",
        "robt_id": "0"
    }


    response = requests.get("http://8.217.172.116:5000/api/session/mine", headers=headers)
    print(response.json())

def add_message(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "text": "你好啊!",
        "robt_id": "0",
        "session_id":"1"
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
        "session_id":13,
        # "context_id":21,
        "page":1,
        "limit":10
    }
    response = requests.get("http://8.217.172.116:5000/api/message", headers=headers,params=data)
    print(response.json())

if __name__ == '__main__':
    # register()
    token = login("user1")
    my_session(token)