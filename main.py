from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
import os
from flask import Flask, request
from keep_alive import keep_alive  # 保活
import threading
import asyncio

VERSION = "v1.0.3"
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
        await update.message.reply_text("dog input /start first")

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

# Flask server
app = Flask(__name__)
application = None

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK"

async def main():
    TOKEN = os.getenv("TOKEN")
    RENDER_URL = os.getenv("RENDER_URL")

    global application
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quit", quit))
    application.add_handler(CommandHandler("version", version))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

    await application.bot.set_webhook(f"{RENDER_URL}/webhook")
    await application.initialize()
    await application.start()
    print(f"Webhook set and application started: {RENDER_URL}/webhook")

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()

    async def runner():
        await main()  # 啟動 application（背景跑）
    
    threading.Thread(target=lambda: asyncio.run(runner()), daemon=True).start()
    
    # 最後啟動 Flask（會阻塞在這裡）
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
