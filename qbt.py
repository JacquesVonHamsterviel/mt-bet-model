import requests

QB_URL = "https://qbn.xxx.com"
USERNAME = "axxxxx"
PASSWORD = "abbbbbb"

session = requests.Session()
session.post(f"{QB_URL}/api/v2/auth/login", data={"username": USERNAME, "password": PASSWORD})

response = session.get(f"{QB_URL}/api/v2/torrents/info")
downloading = [t for t in response.json() if t["state"] == "downloading"]  # 仅删除正在下载的

for t in downloading:
    print(f"停止并删除: {t['name']}")
    session.post(f"{QB_URL}/api/v2/torrents/delete", data={"hashes": t["hash"], "deleteFiles": "true"})
