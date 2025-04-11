import requests
import json, os
import time
from datetime import datetime, timezone
import uuid

def filter_free(torrents):
    free_torrents = [torrent for torrent in torrents if torrent.get("discount") == "FREE"]
    return json.dumps(free_torrents, indent=2, ensure_ascii=False)

def filter_seeders(torrents, min_seeders_num="1"):
    res_torrents = [torrent for torrent in torrents if int(torrent.get("seeders"))>=int(min_seeders_num)]
    return json.dumps(res_torrents, indent=2, ensure_ascii=False)


def filter_size(torrents, size_limit="10"): # Unit: GB
    size_limit_bytes = int(float(size_limit) * 1024 * 1024 * 1024)
    
    filtered_torrents = []
    for torrent in torrents:
        size_str = torrent.get("size", "0")

        try:
            size_bytes = int(size_str)
            if size_bytes < size_limit_bytes:
                filtered_torrents.append(torrent)
        except ValueError:
            continue  

    return json.dumps(filtered_torrents, indent=2, ensure_ascii=False)


def filter_time(torrents, min_time_to_not_free="3"):
    min_time_seconds = int(float(min_time_to_not_free) * 3600)
    filtered_torrents = []
    for torrent in torrents:
        discount_end_time = torrent.get("discountEndTime")

        if not discount_end_time:
            continue

        try:
            end_time_obj = datetime.strptime(discount_end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            end_time_timestamp = int(end_time_obj.timestamp())
            now_time = int(str(int(time.time()))[:10])
            #print(f"end_time_timestamp: {end_time_timestamp}, now_timestamp: {now_time}, hrs: {(end_time_timestamp-now_time-8*3600)/3600} hrs")
            if end_time_timestamp - now_time - 8*3600 < min_time_seconds:
                continue
        except ValueError:
            continue

        filtered_torrents.append(torrent)

    return json.dumps(filtered_torrents, indent=2, ensure_ascii=False)


def filter_len(torrents, max_len="5"):
    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    max_len=int(max_len)
    valid_torrents = []
    for torrent in torrents:
        discount_end_time = torrent.get("discountEndTime")

        if not discount_end_time:
            continue

        try:
            end_time_obj = datetime.strptime(discount_end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            end_time_timestamp = int(end_time_obj.timestamp())

            remaining_time = end_time_timestamp - now_timestamp
            valid_torrents.append((remaining_time, torrent))
        except ValueError:
            continue

    valid_torrents.sort(reverse=True, key=lambda x: x[0])
    
    return json.dumps([torrent[1] for torrent in valid_torrents[:max_len]], indent=2, ensure_ascii=False)


class MTeam:
    def __init__(self, auth, did, visitorid):
        self.base_url = "https://api.m-team.cc/api"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
            "Authorization": auth,
            "did": did,
            "visitorid": visitorid,
            "webversion": "1120",
            "dnt": "1",
            "origin": "https://kp.m-team.cc",
            "priority": "u=1, i",
            "referer": "https://kp.m-team.cc/",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132")',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json"
        }

    def list(self, mode="adult", categories=None, visible=1, page_number=1, page_size=100):
        url = f"{self.base_url}/torrent/search"
        payload = {
            "mode": mode,
            "categories": categories or [],
            "visible": visible,
            "pageNumber": page_number,
            "pageSize": page_size
        }
        self.headers.update({"Ts": str(int(time.time()))})
        response = self.session.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            try:
                response_json = response.json()
                if isinstance(response_json.get("data"), dict):
                    data_list = response_json["data"].get("data", [])
                else:
                    return {"error": "Unexpected response format"}
                if not isinstance(data_list, list):
                    return {"error": "Data format is not a list"}
                result = []
                for item in data_list:
                    if isinstance(item, dict) and "status" in item:
                        result.append({
                            "name": item.get("name", "N/A"),
                            "size": item.get("size", "N/A"),
                            "id": item["status"].get("id", "N/A"),
                            "discount": item["status"].get("discount", "N/A"),
                            "discountEndTime": item["status"].get("discountEndTime", "2025-01-01 12:30:00"),
                            "seeders": item["status"].get("seeders", "0"),
                            "leechers": item["status"].get("leechers", "0")
                        })
                #print(json.dumps(result, indent=2, ensure_ascii=False))
                return result
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response"}

            except json.JSONDecodeError:
                return {"error": "Invalid JSON response"}


        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}

    def download(self, torrent_id, download_path="tmp"):
        url = f"https://api2.m-team.cc/api/torrent/genDlToken"  
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"  

        self.headers.update({
            "Ts": str(int(time.time())),
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "did": self.headers.get("did", ""),
            "visitorid": self.headers.get("visitorid", ""),
            "webversion": "1120"
        })

        payload = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"id\"\r\n\r\n"
            f"{torrent_id}\r\n"
            f"--{boundary}--\r\n"
        )

        response = self.session.post(url, headers=self.headers, data=payload)

        if response.status_code == 200:
            try:
                response_json = response.json()
                if response_json.get("message") == "SUCCESS" and "data" in response_json:
                    download_url = response_json["data"]
                    
                    if not os.path.exists(download_path):
                        os.makedirs(download_path)

                    filename = f"{torrent_id}.torrent"
                    file_path = os.path.join(download_path, filename)

                    torrent_response = requests.get(download_url, stream=True)
                    if torrent_response.status_code == 200:
                        with open(file_path, "wb") as f:
                            for chunk in torrent_response.iter_content(chunk_size=1024):
                                f.write(chunk)
                        print(f"Downloaded {filename} to {download_path}")
                        return file_path
                    else:
                        print(f"Failed to download torrent file: HTTP {torrent_response.status_code}")
                        return None
                else:
                    print(f"Unexpected JSON response: {response_json}")
                    return None
            except requests.exceptions.JSONDecodeError:
                print("Invalid JSON response")
                return None
        else:
            print(f"HTTP {response.status_code}: {response.text}")
            return None


if __name__=="__main__":
    # Here is only for test
    auth_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJmbU04YmtDUSIsInVpZCI6MjczMTUyLCJqdGkiOiJjMTFmNDU4NS1jYzdmLTQ0NzItYmZhOC0yMDU0NTYxYzBiODciLCJpc3MiOiJodHRwczovL2FwaS5tLXRlYW0uaW8iLCJpYXQiOjE3Mzc4MjU3NDYsImV4cCI6MTc0MDQxNzc0Nn0.4p5sHMRB6oCZn67xnx0vLvqqAmL1OfNF7eelEKAVB5j1BWi9DIOTBDQmJ_QR2kcDt0VrcBa8h_JEh0rb2BwplA"
    did="aff75d136fe346a9ad85ca5aedd43d0c"
    visitorid="e82a181335dbbd0a3a9f0c4a63d02410"
    mteam = MTeam(auth_token, did, visitorid)
    '''
    torrents = mteam.list()
    #print(json.dumps(torrents, indent=2, ensure_ascii=False))

    free_torrents_json = filter_free(torrents)
    #print(free_torrents_json)

    filtered_torrents_json = filter_size(torrents, size_limit="10")
    #print(filtered_torrents_json)

    filtered_torrents_json = filter_time(torrents, min_time_to_not_free="5")
    #print(filtered_torrents_json)

    filtered_torrents_json = filter_len(torrents, max_len="5")
    print(filtered_torrents_json)
    # 下载某个种子
    #download_info = mteam.download(torrent_id="123456")
    #print(json.dumps(download_info, indent=2, ensure_ascii=False))
    '''
    #print(mteam.download(906462))
