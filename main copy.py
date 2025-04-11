import os
import json
import requests
from mteam_api import MTeam, filter_free, filter_size, filter_time, filter_len, filter_seeders
from config import *

def download_torrents(mteam, torrents, download_path="download"):
    """ 直接下载种子到 download_path """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    for torrent in torrents:
        torrent_id = torrent.get("id")
        if not torrent_id:
            continue

        file_path = mteam.download(torrent_id, download_path=download_path)
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
        filtered_torrents = json.loads(filter_size(free_torrents, size_limit="20"))
        print(f"🔹 过滤大小 (<=20GB): {len(free_torrents)} => {len(filtered_torrents)}")

        # 过滤时间
        filtered_torrents = json.loads(filter_time(filtered_torrents, min_time_to_not_free="3"))
        print(f"🔹 过滤时间 (至少 3 小时可免费下载): {len(free_torrents)} => {len(filtered_torrents)}")


        filtered_torrents=json.loads(filter_seeders(torrents=filtered_torrents, min_seeders_num="1"))
        # 过滤最大数量
        filtered_torrents = json.loads(filter_len(filtered_torrents, max_len="15"))
        print(f"🔹 过滤最大下载数 (最多 15 个): {len(filtered_torrents)}")

        # 下载最终过滤后的种子
        download_torrents(mteam, filtered_torrents, download_path=download_path)
