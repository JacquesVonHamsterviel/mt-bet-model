import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset

# 1️⃣ 选择 GPU 训练
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"✅ 当前设备: {device}")

# 2️⃣ 加载 tokenizer 和 model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token  # 解决 padding 问题
model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)  # 🔥 让 GPT-2 运行在 GPU

# 3️⃣ 读取 JSON 训练数据
dataset = load_dataset("json", data_files="bet_gpt_training.json", split="train")

# 4️⃣ Tokenize 数据
def tokenize_function(data):
    input_text = f"赔率列表: {data['odds_list']} 预测胜利赔率:"
    output_text = str(data["winner_odds"])
    full_text = input_text + " " + output_text
    return tokenizer(full_text, padding="max_length", truncation=True, max_length=128)

tokenized_dataset = dataset.map(tokenize_function)

# 5️⃣ 启用 GPU 训练
training_args = TrainingArguments(
    output_dir="./bet_gpt2_model",
    per_device_train_batch_size=16,  # 🔥 增大 batch_size，提高 GPU 计算效率
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    save_steps=500,
    logging_steps=100,
    learning_rate=5e-5,
    weight_decay=0.01,
    save_total_limit=2,
    eval_strategy="no",
    fp16=True,  # 🔥 启用混合精度训练，加速计算
)

trainer = Trainer(
    model=model,  # 使用 GPU 训练的模型
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

# 6️⃣ 训练模型
trainer.train()
trainer.save_model("./bet_gpt2_model")
tokenizer.save_pretrained("./bet_gpt2_model")

print("✅ GPT-2 训练完成，已保存！")
