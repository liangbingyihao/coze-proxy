import requests

# url = "http://8.217.172.116:5000/api/auth/register"
# data = {
#     "username": "user1",
#     "email": "user1@163.com",
#     "password": "123456"
# }

# response = requests.post(url, json=data)
# print(response.text)

url = "http://8.217.172.116:5000/api/auth/login"
data = {
    "username": "user1",
    "password": "123456"
}

response = requests.post(url, json=data)
token = response.json().get("data").get("access_token")
print(response.text,token)


headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get("http://8.217.172.116:5000/api/auth/me", headers=headers)
print(response.json())
