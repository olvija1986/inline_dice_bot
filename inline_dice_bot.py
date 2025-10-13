import os
import random
import uuid
import asyncio
from fastapi import FastAPI
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

# ===== Переменные окружения =====
TOKEN = os.environ.get("TOKEN")
PORT = int(os.environ.get("PORT", 10000))  # Render назначает порт в $PORT

# ===== FastAPI для Render =====
fastapi_app = FastAPI()

@fastapi_app.get("/")
async def root():
    return {"status": "ok"}  # простой эндпоинт для проверки работы сервиса

# ===== Telegram бот =====
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

# ===== Создаём Telegram приложение =====
tg_app = ApplicationBuilder().token(TOKEN).build()
tg_app.add_handler(InlineQueryHandler(inline_roll))

# ===== Запуск Telegram polling в фоне =====
@fastapi_app.on_event("startup")
async def startup_event():
    asyncio.create_task(tg_app.run_polling())

# ===== Запуск через uvicorn (для Render) =====
# render автоматически вызовет `uvicorn bot:fastapi_app --host 0.0.0.0 --port $PORT`
