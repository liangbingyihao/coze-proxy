import requests

# url = "http://8.217.172.116:5000/api/auth/register"
# data = {
#     "username": "user1",
#     "email": "user1@163.com",
#     "password": "123456"
# }

# response = requests.post(url, json=data)
# print(response.text)

def login():
    url = "http://8.217.172.116:5000/api/auth/login"
    data = {
        "username": "user1",
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

if __name__ == '__main__':
    token = login()
    my_session(token)