from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes
import random, uuid, os, threading
from fastapi import FastAPI
import uvicorn

# ================== Telegram Token ==================
TOKEN = os.environ.get("TOKEN")

# ================== Inline-запросы ==================
async def inline_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return

    try:
        max_num = int(query)
        if max_num < 1:
            return

        # Генерируем случайное число
        result = random.randint(1, max_num)
        text = f"🎲 Выпало: {result} из {max_num}"

        # Возвращаем inline-результат
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

# ================== Telegram App ==================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(InlineQueryHandler(inline_roll))

# ================== Web Server (для Render) ==================
web_app = FastAPI()

@web_app.get("/")
def home():
    return {"status": "ok", "message": "🎲 Inline Dice Bot is running!"}

def run_bot():
    app.run_polling()

if __name__ == "__main__":
    # Запускаем Telegram-бота в отдельном потоке
    threading.Thread(target=run_bot, daemon=True).start()

    # Запускаем FastAPI-сервер
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(web_app, host="0.0.0.0", port=port)
