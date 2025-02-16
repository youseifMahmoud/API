import requests

url = "http://127.0.0.1:8000/sign-in/"
data = {"username": "user", "password": "password123"}
response = requests.post(url, data=data)
print(response.status_code, response.text)
