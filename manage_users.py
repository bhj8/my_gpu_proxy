import sys

import requests

BASE_URL = "http://localhost:8080"

def add_user(target_url):
    response = requests.post(f"{BASE_URL}/add_user", data={"url": target_url})
    if response.status_code == 200:
        user_info = response.json()
        print(f"User added: {user_info['user_id']} with URL: {user_info['url']}")
    else:
        print("Error adding user:", response.json())

def remove_user(user_id):
    response = requests.post(f"{BASE_URL}/remove_user/{user_id}")
    if response.status_code == 200:
        print(response.text)
    else:
        print("Error removing user:", response.text)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python manage_users.py <add|remove> <url|user_id>")
        sys.exit(1)

    action = sys.argv[1]
    if action == "add":
        target_url = sys.argv[2]
        add_user(target_url)
    elif action == "remove":
        user_id = sys.argv[2]
        remove_user(user_id)
    else:
        print("Invalid action. Use 'add' or 'remove'.")
