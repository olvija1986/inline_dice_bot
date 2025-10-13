import os
import random
import uuid
from fastapi import FastAPI, Request
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes

TOKEN = os.environ["TOKEN"]
WEBHOOK_PATH = f"/webhook/{TOKEN}"
BOT_URL = f"https://<your-render-url>{WEBHOOK_PATH}"

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
                    input_message_content=InputTextMessageContent(text)
                )
            ],
            cache_time=0
        )
    except ValueError:
        await update.inline_query.answer(results=[])

bot_app.add_handler(InlineQueryHandler(inline_roll))

# ================== Webhook endpoint ==================
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.update_queue.put(update)
    return {"ok": True}

# ================== Startup Event ==================
@app.on_event("startup")
async def startup_event():
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.bot.set_webhook(BOT_URL)
    print("✅ Bot started")

# ================== Стартовая страница ==================
@app.get("/")
def root():
    return {"status": "Bot is running ✅"}
