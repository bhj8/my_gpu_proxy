import sys

import requests

SERVER_URL = "http://localhost:8080"

def add_user(url):
    response = requests.post(f"{SERVER_URL}/add_user", json={"url": url})
    if response.status_code == 200:
        print("User added successfully:")
        print(response.json())
    else:
        print("Error adding user:", response.text)

def remove_user(user_id):
    response = requests.post(f"{SERVER_URL}/remove_user/{user_id}")
    if response.status_code == 200:
        print("User removed successfully.")
    else:
        print("Error removing user:", response.text)

def list_users():
    response = requests.get(f"{SERVER_URL}/list_users")
    if response.status_code == 200:
        print("List of running users:")
        for user_id in response.json()["users"]:
            print(f"  {user_id}")
    else:
        print("Error listing users:", response.text)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python account_manager.py add <url>")
        print("  python account_manager.py remove <user_id>")
        print("  python account_manager.py list")
        sys.exit(1)

    action = sys.argv[1]
    if action == "add":
        if len(sys.argv) < 3:
            print("Please provide a URL.")
            sys.exit(1)
        url = sys.argv[2]
        add_user(url)
    elif action == "remove":
        if len(sys.argv) < 3:
            print("Please provide a user_id.")
            sys.exit(1)
        user_id = sys.argv[2]
        remove_user(user_id)
    elif action == "list":
        list_users()
    else:
        print("Invalid action. Use 'add', 'remove', or 'list'.")

if __name__ == "__main__":
    main()

# # 添加用户
# python account_manager.py add https://example.com/

# # 删除用户
# python account_manager.py remove aBcDeFgHiJ

# # 查询所有运行的帐户
# python account_manager.py list
