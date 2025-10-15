import os
import random
import uuid
import asyncio
import httpx
from fastapi import FastAPI, Request
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    InlineQueryHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================== Настройки ==================
TOKEN = os.environ.get("TOKEN")  # токен бота
BOT_URL = os.environ.get("BOT_URL")  # например: https://inline-dice-bot-7xye.onrender.com
WEBHOOK_PATH = f"/webhook/{TOKEN}"

if not TOKEN or not BOT_URL:
    raise RuntimeError("Не заданы переменные окружения TOKEN или BOT_URL")

# ================== FastAPI ==================
app = FastAPI()
bot_app = ApplicationBuilder().token(TOKEN).build()

# ================== Inline-запрос ==================
async def inline_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return

    # --- Логика: случайный выбор ✅ или ❌ ---
    if query == "?":
        result_emoji = random.choice(["✅", "❌"])
        text = f"{result_emoji}"
        await update.inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="✅❌ Случайный выбор",
                    description="Получи ответ — да или нет",
                    input_message_content=InputTextMessageContent(text),
                    thumb_url="https://png.klev.club/uploads/posts/2024-03/png-klev-club-p-vopros-png-6.png",
                )
            ],
            cache_time=0,
        )
        return

    # --- Логика: если введено число 6 — показать кнопку броска кубика ---
    if query == "6":
        text = "🎲 Хочешь бросить настоящий кубик?"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎲 Бросить кубик", callback_data="roll_dice")]]
        )
        await update.inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="🎲 Кубик",
                    description="Случайная кость (нажми кнопку)",
                    input_message_content=InputTextMessageContent(text),
                    reply_markup=keyboard,
                    thumb_url="https://cdn-icons-png.flaticon.com/512/4100/4100836.png",
                )
            ],
            cache_time=0,
        )
        return

    # --- Обычная логика: генерируем случайное число ---
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
                    thumb_url="https://cdn-icons-png.flaticon.com/512/4100/4100836.png",
                )
            ],
            cache_time=0,
        )
    except ValueError:
        await update.inline_query.answer(
            results=[],
            switch_pm_text="Введите число, например: 100",
            switch_pm_parameter="start",
        )


# ================== Callback: бросок кубика ==================
async def handle_dice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # закрываем "загрузка..."
    await context.bot.send_dice(chat_id=query.message.chat.id, emoji="🎲")


# ================== Регистрация хендлеров ==================
bot_app.add_handler(InlineQueryHandler(inline_roll))
bot_app.add_handler(CallbackQueryHandler(handle_dice_callback, pattern="^roll_dice$"))

# ================== Webhook endpoint ==================
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.update_queue.put(update)
    return {"ok": True}

# ================== Lifespan ==================
@app.on_event("startup")
async def startup_event():
    await bot_app.initialize()
    await bot_app.bot.set_webhook(f"{BOT_URL}{WEBHOOK_PATH}")
    await bot_app.start()
    print("✅ Webhook установлен, бот готов к работе")

    async def ping_self():
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    await client.get(BOT_URL)
                except Exception as e:
                    print(f"Ping error: {e}")
                await asyncio.sleep(600)

    asyncio.create_task(ping_self())


@app.on_event("shutdown")
async def shutdown_event():
    await bot_app.stop()
    await bot_app.shutdown()
    print("🛑 Бот остановлен")


# ================== Стартовая страница ==================
@app.get("/")
def root():
    return {"status": "Bot is running ✅"}
