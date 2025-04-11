import sqlite3
import json

# 连接数据库并加载数据
def load_bet_data():
    conn = sqlite3.connect("bet_sort.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.id AS gameid, bo.odds, b.optionid, bo.id
        FROM bets b
        JOIN bet_options bo ON b.id = bo.gameid
        ORDER BY b.id ASC, bo.id ASC;
    """)

    raw_data = cursor.fetchall()
    conn.close()

    # 组织数据
    data = {}
    for gameid, odds, winner_option, option_id in raw_data:
        if winner_option is None:  # 跳过无胜利选项的比赛
            continue

        if gameid not in data:
            data[gameid] = {"odds_list": [], "winner_odds": None}
        
        data[gameid]["odds_list"].append(odds)  # 添加赔率列表

        if option_id == winner_option:
            data[gameid]["winner_odds"] = odds  # 记录胜出的赔率

    # 生成最终的训练数据
    training_data = [
        {"odds_list": game["odds_list"], "winner_odds": game["winner_odds"]}
        for game in data.values()
        if game["winner_odds"] is not None  # 确保每场比赛都有胜利赔率
    ]

    return training_data

# 生成训练数据并存储到 JSON 文件
training_data = load_bet_data()
with open("bet_gpt_training.json", "w") as f:
    json.dump(training_data, f, indent=4)
print(f"✅ 训练数据已正确保存，包含 {len(training_data)} 场比赛赔率信息")
