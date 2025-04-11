import os
import shutil
import json
import requests
from mteam_api import MTeam, filter_free, filter_size, filter_time, filter_len

auth_token = "eyJh"
did = "xxxx"
visitorid = "xxxxx"
download_path = "download"
tmp_path = "tmp"

def download_torrents(mteam, torrents, download_path="download", tmp_path="tmp"):
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    for torrent in torrents:
        torrent_id = torrent.get("id")
        if not torrent_id:
            continue

        file_path = mteam.download(torrent_id, download_path=tmp_path)
        if not file_path:
            print(f"Failed to download torrent {torrent_id}")
            continue

        filename = os.path.basename(file_path)
        final_file_path = os.path.join(download_path, filename)

        if os.path.exists(final_file_path):
            os.remove(file_path)
            print(f"File {filename} already exists in {download_path}. Deleted tmp file.")
        else:
            shutil.move(file_path, final_file_path)
            print(f"Moved {filename} to {download_path}")

if __name__ == "__main__":
    mteam = MTeam(auth_token, did, visitorid)

    torrents = mteam.list()
    if isinstance(torrents, dict) and "error" in torrents:
        print(f"Error fetching torrents: {torrents['error']}")
    else:
        free_torrents = json.loads(filter_free(torrents))
        filtered_torrents = json.loads(filter_size(free_torrents, size_limit="10"))
        filtered_torrents = json.loads(filter_time(filtered_torrents, min_time_to_not_free="5"))
        filtered_torrents = json.loads(filter_len(filtered_torrents, max_len="5"))

        download_torrents(mteam, filtered_torrents, download_path=download_path, tmp_path=tmp_path)
