import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=443, log_level="info", ssl_keyfile="ssl/privkey.pem", ssl_certfile="ssl/fullchain.pem")
