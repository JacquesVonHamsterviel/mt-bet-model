import sqlite3
import numpy as np
from scipy.stats import skew, kurtosis
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# 1️⃣ 读取数据
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
    
    data = {}
    for gameid, odds, winner_option, option_id in raw_data:
        if winner_option is None:  # 忽略没有 Winner 的比赛
            continue
        
        if gameid not in data:
            data[gameid] = {"odds": [], "winner_odds": None}
        data[gameid]["odds"].append(odds)

        if option_id == winner_option:
            data[gameid]["winner_odds"] = odds  # 确保 winner_odds 正确

    return list(data.values())

# 2️⃣ 处理数据
def prepare_data():
    raw_data = load_bet_data()
    
    X, y = [], []
    for game in raw_data:
        odds = sorted(game["odds"])  # 确保赔率排序一致
        if game["winner_odds"] is not None:
            odds_array = np.array(odds)

            # 🔥 解决 precision loss 问题
            if np.all(odds_array == odds_array[0]):  # 如果所有赔率相同
                skew_value = 0.0
                kurtosis_value = 0.0
            else:
                skew_value = skew(odds_array)
                kurtosis_value = kurtosis(odds_array)

            X.append([
                len(odds),              # 选项个数
                np.mean(odds),          # 赔率均值
                np.std(odds),           # 赔率标准差
                np.min(odds),           # 最小赔率
                np.max(odds),           # 最大赔率
                np.median(odds),        # 赔率中位数
                np.max(odds) - np.min(odds),  # 赔率范围
                skew_value,             # 🔥 赔率偏态（修正）
                kurtosis_value,         # 🔥 赔率峰度（修正）
                np.var(odds),           # 赔率方差
                np.abs(np.min(odds) - np.mean(odds)),  # 最小赔率与均值的偏差
                np.abs(np.max(odds) - np.mean(odds)),  # 最大赔率与均值的偏差
                odds[0],                # 最小赔率（排序后）
                odds[-1]                # 最大赔率（排序后）
            ])
            y.append(game["winner_odds"])
    
    return np.array(X), np.array(y)

# 3️⃣ 训练模型
def train_model():
    X, y = prepare_data()
    
    print("\n📊 训练数据样本 (前 5 条)：")
    for i in range(min(5, len(X))):  # 仅打印前 5 条数据
        print(f"X[{i}] = {X[i]}, y[{i}] = {y[i]}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    error = mean_absolute_error(y_test, y_pred)
    print(f"\n🎯 模型训练完成，测试集 MAE 误差: {error:.4f}")
    
    return model

# 4️⃣ 预测新的比赛胜利赔率
def predict_winner_odds(model, odds_list):
    odds_list = sorted(odds_list)  # 确保顺序一致
    odds_array = np.array(odds_list)

    X_new = np.array([[
        len(odds_list),
        np.mean(odds_list),
        np.std(odds_list),
        np.min(odds_list),
        np.max(odds_list),
        np.median(odds_list),
        np.max(odds_list) - np.min(odds_list),
        skew(odds_array),
        kurtosis(odds_array),
        np.var(odds_list),
        np.abs(np.min(odds_list) - np.mean(odds_list)),
        np.abs(np.max(odds_list) - np.mean(odds_list)),
        odds_list[0],
        odds_list[-1]
    ]])

    print("\n🧐 预测数据输入：")
    print(f"  赔率列表: {odds_list}")
    print(f"  特征向量: {X_new[0]}")

    predicted_odds = model.predict(X_new)[0]

    # 🔥 让预测结果落在赔率列表中
    closest_odds = min(odds_list, key=lambda x: abs(x - predicted_odds))

    print(f"\n🏆 原始预测: {predicted_odds:.2f}，最终调整为: {closest_odds:.2f}")
    return closest_odds

# 5️⃣ 运行
if __name__ == "__main__":
    model = train_model()

    # 测试新赔率预测
    test_odds = [1.5, 2.3, 3.0, 1.8]  # 传入一个新的比赛赔率列表
    #test_odds = [2.6, 1.68] 
    predicted_winner_odds = predict_winner_odds(model, test_odds)
    print(f"\n🏆 预测最可能的胜利赔率: {predicted_winner_odds:.2f}")
