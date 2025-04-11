import os
import json
import requests
from mteam_api import MTeam, filter_free, filter_size, filter_time, filter_len, filter_seeders
from config import *
import sqlite3


DB_FILE = "downloads.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloaded_torrents (
            id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()
#init_db()


def is_downloaded(torrent_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM downloaded_torrents WHERE id = ?", (torrent_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_as_downloaded(torrent_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO downloaded_torrents (id) VALUES (?)", (torrent_id,))
    conn.commit()
    conn.close()


def download_torrents(mteam, torrents, download_path="download"):
    """ 直接下载种子到 download_path """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    for torrent in torrents:
        torrent_id = torrent.get("id")
        if not torrent_id or is_downloaded(torrent_id):
            print(f"⚠️ 已经下载过了，跳过：种子 {torrent_id}")
            continue
        if not torrent_id:
            continue
        
        file_path = mteam.download(torrent_id, download_path=download_path)
        mark_as_downloaded(torrent_id)
        if not file_path:
            print(f"❌ 下载失败：种子 {torrent_id}")
        else:
            print(f"✅ 成功下载：{os.path.basename(file_path)} 到 {download_path}")

if __name__ == "__main__":
    mteam = MTeam(auth_token, did, visitorid)

    torrents = mteam.list()
    if isinstance(torrents, dict) and "error" in torrents:
        print(f"⚠️ 获取种子列表失败: {torrents['error']}")
    else:
        print(f"📥 初始种子数量: {len(torrents)}")

        # 过滤免费种子
        free_torrents = json.loads(filter_free(torrents))
        print(f"🔹 免费种子: {len(torrents)} => {len(free_torrents)}")

        # 过滤大小
        filtered_torrents = json.loads(filter_size(free_torrents, size_limit="8"))
        print(f"🔹 过滤大小 (<=8GB): {len(free_torrents)} => {len(filtered_torrents)}")

        # 过滤时间
        filtered_torrents = json.loads(filter_time(filtered_torrents, min_time_to_not_free="3"))
        print(f"🔹 过滤时间 (至少 3 小时可免费下载): {len(free_torrents)} => {len(filtered_torrents)}")


        filtered_torrents=json.loads(filter_seeders(torrents=filtered_torrents, min_seeders_num="1"))
        # 过滤最大数量
        filtered_torrents = json.loads(filter_len(filtered_torrents, max_len="3"))
        print(f"🔹 过滤最大下载数 (最多 3 个): {len(filtered_torrents)}")

        # 下载最终过滤后的种子
        download_torrents(mteam, filtered_torrents, download_path=download_path)
