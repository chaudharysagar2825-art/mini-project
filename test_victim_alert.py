import requests

BASE_URL = "http://127.0.0.1:8000"

login = requests.post(
    f"{BASE_URL}/auth/login",
    data={
        "username": "testvictim",
        "password": "TestPass123!"
    },
)

print("Login status:", login.status_code)

if login.status_code == 200:
    token = login.json()["access_token"]
    response = requests.get(
        f"{BASE_URL}/alerts/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    print("Alert view status:", response.status_code)
    print("Response:", response.text)