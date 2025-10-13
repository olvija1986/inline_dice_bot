import os
import random
import uuid
from fastapi import FastAPI, Request
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
WEBHOOK_PATH = f"/webhook/{TOKEN}"
BOT_URL = f"https://inline-dice-bot-7xye.onrender.com{WEBHOOK_PATH}"

app = FastAPI()
bot_app = ApplicationBuilder().token(TOKEN).build()

# === Inline-запрос ===
async def inline_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return
    try:
        max_num = int(query)
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

# === Webhook endpoint ===
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.update_queue.put(update)
    return {"ok": True}

# === Стартовая страница ===
@app.get("/")
def root():
    return {"status": "Bot is running ✅"}
