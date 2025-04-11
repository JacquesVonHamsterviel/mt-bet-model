import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# 1️⃣ 选择 GPU 运行
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"✅ 当前设备: {device}")

# 2️⃣ 加载训练好的 GPT-2 模型
model_path = "./bet_gpt2_model"  # 确保路径正确
model = GPT2LMHeadModel.from_pretrained(model_path).to(device)
tokenizer = GPT2Tokenizer.from_pretrained(model_path)

# 3️⃣ 赔率预测函数
def predict_winner_odds(odds_list):
    input_text = f"赔率列表: {odds_list} 预测胜利赔率:"
    inputs = tokenizer(input_text, return_tensors="pt").to(device)

    # 生成文本
    output = model.generate(**inputs, max_length=128, num_return_sequences=1)
    prediction = tokenizer.decode(output[0], skip_special_tokens=True)

    print(f"\n📝 GPT 生成的完整输出: {prediction}")

    # 解析 GPT 预测的赔率
    predicted_odds = None
    try:
        if "预测胜利赔率:" in prediction:
            predicted_odds = float(prediction.split("预测胜利赔率:")[-1].strip())
        else:
            print("⚠ GPT 生成的结果没有包含赔率，回退到默认策略。")
            predicted_odds = odds_list[0]  # 如果解析失败，默认返回最低赔率
    except ValueError:
        print("⚠ 无法解析 GPT 预测的赔率，回退到默认策略。")
        predicted_odds = odds_list[0]  # 避免崩溃

    # 🔥 确保预测的赔率在输入赔率范围内
    closest_odds = min(odds_list, key=lambda x: abs(x - predicted_odds))

    print(f"\n🏆 GPT 预测: {predicted_odds:.2f}，最终调整为: {closest_odds:.2f}")
    return closest_odds

# 4️⃣ 测试新的赔率预测
#test_odds = [1.5, 2.3, 3.0, 1.8]  # 你可以换成新的赔率列表
test_odds = [1.86, 2.17]  
predicted_winner_odds = predict_winner_odds(test_odds)

print(f"\n🏆 最可能的胜利赔率: {predicted_winner_odds:.2f}")
