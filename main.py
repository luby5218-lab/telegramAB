from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
import os
from flask import Flask
import threading

VERSION = "v1.0.1"  # 版本號

# 用來存不同用戶的遊戲答案
user_games = {}

# 產生隨機不重複的四位數
def generate_answer():
    digits = list(range(0, 10))
    ans = ""
    for _ in range(4):
        a = random.choice(digits)
        ans += str(a)
        digits.remove(a)
    return ans

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    answer = generate_answer()
    user_games[user_id] = answer
    await update.message.reply_text("1234 ?A?B\nGuess")

# /quit
async def quit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = user_games[user_id]
    await update.message.reply_text(f"It's {answer}\ntry harder dog")

# 處理使用者輸入的猜測
async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    guess = update.message.text.strip()

    # 如果使用者沒有先 /start
    if user_id not in user_games:
        await update.message.reply_text("dog input /start")
        return

    answer = user_games[user_id]

    # 輸入必須是 4 位數字
    if not guess.isdigit() or len(guess) != 4:
        await update.message.reply_text("4 digits dog")
        return

    # 判斷幾 A 幾 B
    A = sum(1 for i in range(4) if answer[i] == guess[i])
    B = sum(1 for i in range(4) for j in range(4) if i != j and answer[i] == guess[j])

    if A == 4:
        await update.message.reply_text(f"Yeah {answer}")
        del user_games[user_id]  # 清除遊戲
    else:
        await update.message.reply_text(f"{A}A{B}B")

# /version
async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Current bot version: {VERSION}")

# Flask server for Render ping
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def run_bot():
    TOKEN = os.getenv("TOKEN")
    application = Application.builder().token(TOKEN).build()

    # 指令處理
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("version", version))
    application.add_handler(CommandHandler("quit", quit))

    # 處理文字
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

    print("Telegram Bot started!", flush=True)
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
