import json
import urllib.request
import urllib.error

try:
    login_data = json.dumps({
        "username": "testadmin",
        "password": "AdminPass123!"
    }).encode()

    login_request = urllib.request.Request(
        "http://127.0.0.1:8000/auth/login",
        data=login_data,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(login_request, timeout=5) as response:
        token = json.loads(response.read())["access_token"]

    action_data = json.dumps({
        "action": "resolve",
        "reason": "Synthetic development permission test"
    }).encode()

    action_request = urllib.request.Request(
        "http://127.0.0.1:8000/alerts/2/action",
        data=action_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        method="PATCH"
    )

    with urllib.request.urlopen(action_request, timeout=5) as response:
        print("HTTP status:", response.status)
        print("Response:", response.read().decode())

except urllib.error.HTTPError as error:
    print("HTTP status:", error.code)
    print("Response:", error.read().decode())

except Exception as error:
    print("Test error:", str(error))
