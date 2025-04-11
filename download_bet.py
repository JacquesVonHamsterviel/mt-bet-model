import sqlite3
import time
from datetime import datetime
from mteam_api import MTeam
from config import auth_token, did, visitorid

# 初始化数据库
def init_db():
    conn = sqlite3.connect("bets.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY,
        created_date TEXT,
        last_modified_date TEXT,
        heading TEXT,
        undertext TEXT,
        endtime TEXT,
        active TEXT,
        sort INTEGER,
        creator INTEGER,
        fix INTEGER,
        optionid INTEGER,
        countall INTEGER,
        tax_rate REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bet_options (
        id INTEGER PRIMARY KEY,
        gameid INTEGER,
        created_date TEXT,
        last_modified_date TEXT,
        text TEXT,
        odds REAL,
        my_bonus REAL,
        bonus_total REAL,
        FOREIGN KEY (gameid) REFERENCES bets(id)
    )
    """)

    conn.commit()
    conn.close()

# 存储 bet 数据到数据库
def save_bet_data(bet_data):
    conn = sqlite3.connect("bets.db")
    cursor = conn.cursor()

    for bet in bet_data:
        # 插入主表数据
        cursor.execute("""
        INSERT OR REPLACE INTO bets (id, created_date, last_modified_date, heading, undertext, endtime, active, sort, 
                                     creator, fix, optionid, countall, tax_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(bet["id"]),
            bet["createdDate"],
            bet["lastModifiedDate"],
            bet["heading"],
            bet["undertext"],
            bet["endtime"],
            bet["active"],
            int(bet["sort"]),
            int(bet["creator"]),
            int(bet["fix"]),
            int(bet["optionid"]),
            int(bet["countall"]),
            float(bet["taxRate"])
        ))

        # 插入子表数据（投注选项）
        for option in bet.get("optionsList", []):
            cursor.execute("""
            INSERT OR REPLACE INTO bet_options (id, gameid, created_date, last_modified_date, text, odds, my_bonus, bonus_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(option["id"]),
                int(option["gameid"]),
                option["createdDate"],
                option["lastModifiedDate"],
                option["text"],
                float(option["odds"]),
                float(option["myBonus"]),
                float(option["bonusTotal"])
            ))

    conn.commit()
    conn.close()

# 主函数
def main():
    init_db()
    
    mteam = MTeam(auth_token, did, visitorid)

    page = 1
    while True:
        print(f"Fetching page {page}...")
        response = mteam.bet(pagenum=str(page))

        if response.get("message") != "SUCCESS":
            print(f"Failed to fetch bets: {response}")
            break

        bet_list = response.get("data", {}).get("data", [])
        if not bet_list:
            print("No more bets to fetch.")
            break

        save_bet_data(bet_list)

        total_pages = int(response["data"]["totalPages"])
        if page >= total_pages:
            break

        page += 1
        time.sleep(1)  # 避免请求过快

    print("All bet data has been saved.")

if __name__ == "__main__":
    main()

