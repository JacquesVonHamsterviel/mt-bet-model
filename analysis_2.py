import sqlite3
import numpy as np

def kelly_criterion(odds, win_prob):
    """ 计算凯利公式投注比例 """
    b = odds - 1  # 计算净赔率
    f_star = (b * win_prob - (1 - win_prob)) / b
    return max(0, min(f_star, 1))  # 确保投注比例在 0 到 1 之间

def calculate_profit(amount=10000, recent=100, debug=False):
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
    
    win_counts = {}  # 统计不同赔率的胜率
    total_counts = {}
    
    for game in games:
        sorted_odds = sorted(game["odds"], key=lambda x: x[0])  # 按赔率排序
        min_odds, min_option = sorted_odds[0]  # 选择最低赔率的队伍
        
        if min_odds not in win_counts:
            win_counts[min_odds] = 0
            total_counts[min_odds] = 0
        
        total_counts[min_odds] += 1
        if min_option == game["winner_id"]:
            win_counts[min_odds] += 1
    
    # 计算赔率对应的历史胜率
    win_probabilities = {odds: win_counts[odds] / total_counts[odds] for odds in win_counts}
    
    for game in games:
        sorted_odds = sorted(game["odds"], key=lambda x: x[0])
        min_odds, min_option = sorted_odds[0]
        win_prob = win_probabilities.get(min_odds, 0.5)  # 如果没有历史数据，假设50%胜率
        bet_fraction = kelly_criterion(min_odds, win_prob)
        bet_amount = bet_fraction * amount  # 计算最佳投注金额
        
        if debug:
            print(f"🎲 比赛: 赔率={min_odds:.2f}, 胜率={win_prob:.2f}, 投注比例={bet_fraction:.2f}, 投注金额={bet_amount:.2f}")
        
        total_bet += bet_amount
        if min_option == game["winner_id"]:
            total_win += bet_amount * min_odds  # 赢得金额
    
    profit = total_win - total_bet
    
    print(f"💰 总投注金额: {total_bet:.2f}")
    print(f"🏆 总赢得金额: {total_win:.2f}")
    print(f"📊 最终盈亏: {profit:.2f}")
    
    return profit

# 运行计算
if __name__ == "__main__":
    calculate_profit(amount=10000, recent=100, debug=True)
