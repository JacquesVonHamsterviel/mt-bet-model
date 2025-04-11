import sqlite3
import numpy as np

def calculate_profit(amount=10000, recent=100):
    # 连接数据库
    conn = sqlite3.connect("bet_sort.db")
    cursor = conn.cursor()
    
    # 获取最近 recent 场比赛数据
    cursor.execute("""
        SELECT b.id AS gameid, bo.odds, b.optionid, bo.id
        FROM bets b
        JOIN bet_options bo ON b.id = bo.gameid
        WHERE b.optionid IS NOT NULL  -- 确保有获胜者
        ORDER BY b.id DESC, bo.id ASC
        LIMIT ?;
    """, (recent * 2,))  # 乘以2 以确保足够的比赛数据
    
    raw_data = cursor.fetchall()
    conn.close()
    
    data = {}
    for gameid, odds, winner_option, option_id in raw_data:
        if gameid not in data:
            data[gameid] = {"odds": [], "winner_odds": None, "winner_id": winner_option}
        data[gameid]["odds"].append((odds, option_id))
        
    # 仅保留 recent 场比赛
    games = list(data.values())[:recent]
    
    total_bet = 0
    total_win = 0
    
    for game in games:
        sorted_odds = sorted(game["odds"], key=lambda x: x[0])  # 按赔率排序
        min_odds, min_option = sorted_odds[0]  # 选择最低赔率的队伍
        
        total_bet += amount  # 每场下注 amount
        if min_option == game["winner_id"]:
            total_win += amount * min_odds  # 赢得金额
    
    profit = total_win - total_bet
    
    print(f"💰 总投注金额: {total_bet:.2f}")
    print(f"🏆 总赢得金额: {total_win:.2f}")
    print(f"📊 最终盈亏: {profit:.2f}")
    
    return profit

# 运行计算
if __name__ == "__main__":
    calculate_profit(amount=10000, recent=100)
