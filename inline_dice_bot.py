import os
import random
import uuid
from fastapi import FastAPI, Request
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

# ================== Настройки ==================
TOKEN = os.environ["TOKEN"]  # токен бота
BOT_URL = os.environ.get("BOT_URL")  # например: https://inline-dice-bot-7xye.onrender.com
WEBHOOK_PATH = f"/webhook/{TOKEN}"

if not TOKEN:
    raise RuntimeError("Не задана переменная окружения TOKEN")
if not BOT_URL:
    raise RuntimeError("Не задана переменная окружения BOT_URL")

# ================== FastAPI ==================
app = FastAPI()
bot_app = ApplicationBuilder().token(TOKEN).build()

# ================== Inline-запрос ==================
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

# ================== Webhook endpoint ==================
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """Обрабатываем обновления от Telegram через webhook"""
    data = await request.json()
    update = Update.de_json(data, bot=bot_app.bot)  # ⚡ PTB v20+
    await bot_app.update_queue.put(update)
    return {"ok": True}

# ================== Lifespan: установка webhook при старте ==================
@app.on_event("startup")
async def startup_event():
    await bot_app.bot.set_webhook(f"{BOT_URL}{WEBHOOK_PATH}")
    print("✅ Webhook установлен, бот готов к работе")

# ================== Стартовая страница ==================
@app.get("/")
def root():
    return {"status": "Bot is running ✅"}
