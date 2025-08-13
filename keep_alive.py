from flask import Flask
from threading import Thread
import requests
import time
import os

def ping_self():
    url = os.getenv("RENDER_URL")
    if not url:
        print("RENDER_URL not set, skipping ping")
        return
    while True:
        try:
            requests.get(url)
            print(f"[KeepAlive] Pinged {url}")
        except Exception as e:
            print(f"[KeepAlive] Ping failed: {e}")
        time.sleep(600)  # 每 10 分鐘 ping 一次

def keep_alive():
    Thread(target=ping_self, daemon=True).start()
