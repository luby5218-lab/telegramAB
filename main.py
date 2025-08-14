from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import random
import os
from flask import Flask, request as flask_request
from keep_alive import keep_alive  # 保活
from httpx import Timeout

VERSION = "v1.0.5"
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
    user_id = update.effective_user.id
    if user_id in user_games:
        answer = user_games[user_id]
        await update.message.reply_text(f"It's {answer}\ntry harder dog")
        del user_games[user_id]
    else:
        await update.message.reply_text("Cannot /quit before you even /start")

# 猜測邏輯
async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    guess = update.message.text.strip()

    if user_id not in user_games:
        await update.message.reply_text("dog input /start")
        return

    answer = user_games[user_id]

    if not guess.isdigit() or len(guess) != 4:
        await update.message.reply_text("4 digits dog")
        return

    for i in range(3):
        for j in range(i+1, 4):
            if guess[i] == guess[j]:
                await update.message.reply_text("dog that's cheating")
                return

    A = sum(1 for i in range(4) if answer[i] == guess[i])
    B = sum(1 for i in range(4) for j in range(4) if i != j and answer[i] == guess[j])

    if A == 4:
        await update.message.reply_text(f"Yeah {answer}")
        del user_games[user_id]
    else:
        await update.message.reply_text(f"{A}A{B}B")

# /version
async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Current bot version: {VERSION}")

# Flask server (只做 keep alive 用)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    keep_alive()

    TOKEN = os.getenv("TOKEN")
    RENDER_URL = os.getenv("RENDER_URL")

    timeout = Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
    request = HTTPXRequest(connection_pool_size=50, pool_timeout=30.0)

    application = Application.builder().token(TOKEN).request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quit", quit))
    application.add_handler(CommandHandler("version", version))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

    # 直接啟動 webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path="",
        webhook_url=f"{RENDER_URL}",
    )
