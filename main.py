import functools
import os
import random
import string
from ipaddress import ip_address
from typing import Optional

import dotenv
import requests
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from fastapi.routing import APIRoute

dotenv.load_dotenv()  # 读取.env文件中的环境变量
allow_ip = os.getenv("ALLOW_IP")
print(f"Allowed IP: {allow_ip}")  # 输出获取到的环境变量值
app = FastAPI()
app = FastAPI(openapi_url=None, redoc_url=None)


def check_ip(request: Request):
    allowed_ips = [str(allow_ip)]  # 将这里的IP地址更改为您允许访问的IP地址
    client_ip = ip_address(request.client.host)

    for allowed_ip in allowed_ips:
        if client_ip == ip_address(allowed_ip):
            return True

    raise HTTPException(status_code=403, detail="试啥呢试？这点B东西我能想不到？")

def generate_random_string(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

async def handle_proxy_request(request: Request, path: str, target_url: str):
    full_url = f"{target_url}{path}"
    method = request.method
    headers = dict(request.headers)

    if method == "GET":
        resp = requests.get(full_url, params=request.query_params, headers=headers)
    elif method == "POST":
        resp = requests.post(full_url, json=await request.json(), headers=headers)
    elif method == "PUT":
        resp = requests.put(full_url, json=await request.json(), headers=headers)
    elif method == "DELETE":
        resp = requests.delete(full_url, headers=headers)
    else:
        return JSONResponse(content="Unsupported method", status_code=405)

    excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
    response_headers = {name: value for (name, value) in resp.headers.items() if name.lower() not in excluded_headers}
    response = JSONResponse(content=resp.content, status_code=resp.status_code, headers=response_headers)
    return response


class AddUserRequest(BaseModel):
    url: str

class AddUserResponse(BaseModel):
    user_id: str
    url: str

async def user_route(request: Request, path: str = "", user_id: str = "", target_url: str = ""):
    return await handle_proxy_request(request, path, target_url)

@app.post("/add_user", response_model=AddUserResponse, dependencies=[Depends(check_ip)])
async def add_user(request: AddUserRequest):
    target_url = request.url
    if not target_url:
        raise HTTPException(status_code=400, detail="No URL provided")

    user_id = generate_random_string()

    async def user_route(request: Request, path: str = "", user_id: str = user_id, target_url: str = target_url):
        return await handle_proxy_request(request, path, target_url)

    route = APIRoute(
        path=f"/{user_id}/{{path:path}}/",
        endpoint=user_route,
        methods=["GET", "POST", "PUT", "DELETE"],
        dependencies=[Depends(check_ip)],
    )

    app.routes.append(route)
    print(f"Added route: {route.path} -> {route.endpoint}")
    return {"user_id": user_id, "url": target_url}


@app.post("/remove_user/{user_id}", dependencies=[Depends(check_ip)])
async def remove_user(user_id: str):
    for route in app.routes:
        if f"/{user_id}/" in route.path:
            app.routes.remove(route)
            break
    else:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    return f"User {user_id} removed."

@app.get("/list_users", dependencies=[Depends(check_ip)])
async def list_users():
    users = []
    for route in app.routes:
        users.append(route.path)
        # user_id = route.path.split("/", 2)[1]
        # if user_id not in users:
        #     users.append(user_id)
    return {"users": users}



@app.get("/{path:path}")
async def catch_all(path: str):
    return JSONResponse(content={"error": "Not Found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="info")


