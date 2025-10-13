import os
import random
import uuid
import asyncio
from threading import Thread
from contextlib import asynccontextmanager
from fastapi import FastAPI
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

# === Настройки ===
TOKEN = os.environ.get("TOKEN")

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

# === Lifespan API (новый способ) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = Thread(target=lambda: asyncio.run(bot_app.run_polling()), daemon=True)
    thread.start()
    print("✅ Telegram Bot запущен в фоне")
    yield
    print("🛑 Остановка приложения")

# === Инициализация FastAPI ===
app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"status": "Bot is running ✅"}
