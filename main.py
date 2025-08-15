from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import random
import os
from keep_alive import keep_alive  # 保活
from httpx import Timeout

VERSION = "v1.0.5"
user_games = {}

# 隨機產生 4 位不重複數字
def generate_answer():
    digits = list(range(10))
    ans = "".join(str(digits.pop(random.randrange(len(digits)))) for _ in range(4))
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
        answer = user_games.pop(user_id)
        await update.message.reply_text(f"It's {answer}\ntry harder dog")
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

    if len(set(guess)) != 4:
        await update.message.reply_text("dog that's cheating")
        return

    A = sum(answer[i] == guess[i] for i in range(4))
    B = sum(answer[i] != guess[i] and answer[i] in guess for i in range(4))

    if A == 4:
        await update.message.reply_text(f"Yeah {answer}")
        user_games.pop(user_id)
    else:
        await update.message.reply_text(f"{A}A{B}B")

# /version
async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Current bot version: {VERSION}")

if __name__ == "__main__":
    keep_alive()  # 啟動 ping 自己，非阻塞

    TOKEN = os.getenv("TOKEN")
    RENDER_URL = os.getenv("RENDER_URL")

    request = HTTPXRequest(connection_pool_size=20, pool_timeout=30.0)
    application = Application.builder().token(TOKEN).request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quit", quit))
    application.add_handler(CommandHandler("version", version))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}",
    )
