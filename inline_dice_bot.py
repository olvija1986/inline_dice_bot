import os
import random
import uuid
import asyncio
import threading
import requests
import time
from fastapi import FastAPI
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

# === Настройки ===
TOKEN = os.environ.get("TOKEN")

# === FastAPI приложение ===
app = FastAPI()
bot_app = ApplicationBuilder().token(TOKEN).build()

# === Inline логика ===
async def inline_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return

    try:
        max_num = int(query)
        if max_num < 1:
            return

        result = random.randint(1, max_num)
        text = f"🎲 Выпало: {result} из {max_num}"

        await update.inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="🎲 Генерировать число",
                    description="Нажми, чтобы узнать число",
                    input_message_content=InputTextMessageContent(text),
                    thumb_url="https://cdn-icons-png.flaticon.com/512/4100/4100836.png"
                )
            ],
            cache_time=0
        )
    except ValueError:
        await update.inline_query.answer(
            results=[],
            switch_pm_text="Введите число, например: 100",
            switch_pm_parameter="start"
        )

bot_app.add_handler(InlineQueryHandler(inline_roll))

# === Функция для фонового запуска бота ===
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_app.run_polling())

# === Lifespan (новый способ старта) ===
@app.on_event("startup")
async def start_bot():
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    print("✅ Telegram Bot запущен в фоне")

# === Keep-alive пингер, чтобы Render не засыпал ===
def keep_alive():
    url = "https://inline-dice-bot-7xye.onrender.com"  # 🔹 замени на свой Render URL
    while True:
        try:
            requests.get(url)
            print("🔄 Ping sent to Render")
        except Exception as e:
            print(f"⚠️ Ping failed: {e}")
        time.sleep(600)  # каждые 10 минут

threading.Thread(target=keep_alive, daemon=True).start()

@app.get("/")
def home():
    return {"status": "Bot is running ✅"}
