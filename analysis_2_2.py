import sqlite3
import numpy as np

def kelly_criterion(odds, win_prob):
    """ 计算凯利公式投注比例 """
    b = odds - 1  # 计算净赔率
    f_star = (b * win_prob - (1 - win_prob)) / b
    return max(0, min(f_star, 1))  # 确保投注比例在 0 到 1 之间

def get_historical_win_prob(recent=100):
    """ 从数据库获取赔率对应的历史胜率 """
    conn = sqlite3.connect("bet_sort.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT bo.odds, COUNT(*) AS total, SUM(CASE WHEN bo.id = b.optionid THEN 1 ELSE 0 END) AS wins
        FROM bets b
        JOIN bet_options bo ON b.id = bo.gameid
        WHERE b.optionid IS NOT NULL  -- 确保有获胜者
        GROUP BY bo.odds
        ORDER BY bo.odds ASC
        LIMIT ?;
    """, (recent,))
    
    odds_data = cursor.fetchall()
    conn.close()
    
    historical_win_prob = {odds: wins / total if total > 0 else 0.5 for odds, total, wins in odds_data}
    return historical_win_prob

def calculate_profit(amount=10000, recent=100, debug=False):
    historical_win_prob = get_historical_win_prob(recent)
    
    conn = sqlite3.connect("bet_sort.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT b.id AS gameid, bo.odds, b.optionid, bo.id
        FROM bets b
        JOIN bet_options bo ON b.id = bo.gameid
        WHERE b.optionid IS NOT NULL  -- 确保有获胜者
        ORDER BY b.id DESC, bo.id ASC
        LIMIT ?;
    """, (recent * 2,))
    
    raw_data = cursor.fetchall()
    conn.close()
    
    data = {}
    for gameid, odds, winner_option, option_id in raw_data:
        if gameid not in data:
            data[gameid] = {"odds": [], "winner_id": winner_option}
        data[gameid]["odds"].append((odds, option_id))
        
    games = list(data.values())[:recent]
    total_bet = 0
    total_win = 0
    
    for game in games:
        sorted_odds = sorted(game["odds"], key=lambda x: x[0])
        min_odds, min_option = sorted_odds[0]
        win_prob = historical_win_prob.get(min_odds, 0.5)
        bet_fraction = kelly_criterion(min_odds, win_prob)
        bet_amount = bet_fraction * amount
        
        if debug:
            print(f"🎲 赔率={min_odds:.2f}, 胜率={win_prob:.2f}, 投注比例={bet_fraction:.2f}, 投注金额={bet_amount:.2f}")
        
        total_bet += bet_amount
        if min_option == game["winner_id"]:
            total_win += bet_amount * min_odds
    
    profit = total_win - total_bet
    
    print(f"💰 总投注金额: {total_bet:.2f}")
    print(f"🏆 总赢得金额: {total_win:.2f}")
    print(f"📊 最终盈亏: {profit:.2f}")
    return profit

def predict_bet(odds_list, amount=10000, debug=False):
    historical_win_prob = get_historical_win_prob()
    predictions = []
    for odds in odds_list:
        win_prob = historical_win_prob.get(odds, 0.5)
        bet_fraction = kelly_criterion(odds, win_prob)
        bet_amount = bet_fraction * amount
        predictions.append((odds, bet_amount))
        
        if debug:
            print(f"🔮 赔率={odds:.2f}, 胜率={win_prob:.2f}, 投注比例={bet_fraction:.2f}, 投注金额={bet_amount:.2f}")
    
    best_bet = max(predictions, key=lambda x: x[1])
    print(f"🏆 推荐投注: 赔率={best_bet[0]:.2f}, 投注金额={best_bet[1]:.2f}")
    return best_bet

if __name__ == "__main__":
    calculate_profit(amount=10000, recent=100, debug=True)
    test_odds = [1.5, 2.3, 3.0, 1.8]
    predict_bet(test_odds, amount=10000, debug=True)

