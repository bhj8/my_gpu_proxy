import random
import string

import requests
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

BASE_URL = 'https://pfkuptcothrf8n-3000.proxy.runpod.net/'
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
def handle_proxy_request(path, target_url):
    full_url = f"{target_url}{path}"
    if request.method == 'GET':
        resp = requests.get(full_url)
    elif request.method == 'POST':
        resp = requests.post(full_url, json=request.get_json())
    elif request.method == 'PUT':
        resp = requests.put(full_url, json=request.get_json())
    elif request.method == 'DELETE':
        resp = requests.delete(full_url)
    else:
        return Response("Unsupported method", status=405)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response

def proxy_user(path, user_id):
    target_url = BASE_URL # 请根据用户ID生成对应的目标URL
    return handle_proxy_request(path, target_url)

@app.route('/add_user', methods=['POST'])
def add_user():
    target_url = request.form.get('url')  # 从POST请求中获取URL
    if not target_url:
        return jsonify({"error": "No URL provided"}), 400

    user_id = generate_random_string()  # 生成随机字符串作为用户ID
    app.add_url_rule(f'/{user_id}/', f'user_{user_id}', lambda path='': proxy_user(path, user_id))
    app.add_url_rule(f'/{user_id}/<path:path>', f'user_{user_id}_path', lambda path: proxy_user(path, user_id),
                     methods=['GET', 'POST', 'PUT', 'DELETE'])

    return jsonify({"user_id": user_id, "url": target_url})  # 返回用户ID和URL

@app.route('/remove_user/<user_id>', methods=['POST'])
def remove_user(user_id):
    try:
        app.url_map._rules.remove(app.url_map._rules_by_endpoint[f'user_{user_id}'][0])
        app.url_map._rules.remove(app.url_map._rules_by_endpoint[f'user_{user_id}_path'][0])
        del app.url_map._rules_by_endpoint[f'user_{user_id}']
        del app.url_map._rules_by_endpoint[f'user_{user_id}_path']
        return f"User {user_id} removed."
    except KeyError:
        return f"User {user_id} not found."
    
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({"error": "Not Found"}), 404

if __name__ == '__main__':
    app.run(port=8080)

"""
POST /add_user
Content-Type: application/x-www-form-urlencoded

url=https%3A%2F%2Fexample.com%2F


返回的json
{
  "user_id": "aBcDeFgHiJ",
  "url": "https://example.com/"
}

"""

