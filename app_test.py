import requests

url = "http://8.217.172.116:5000/api/auth/register"
data = {
    "username": "testuser1",
    "email": "test@example.com",
    "password": "securepassword123"
}

response = requests.post(url, json=data)
print(response.text)