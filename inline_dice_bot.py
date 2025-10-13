from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes
import random, uuid, os

TOKEN = os.environ.get("TOKEN")

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

        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="🎲 Рандом",
                input_message_content=InputTextMessageContent(text),
            )
        ], cache_time=0)

    except ValueError:
        await update.inline_query.answer([], switch_pm_text="Введите число, например: 100", switch_pm_parameter="start")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(InlineQueryHandler(inline_roll))
app.run_polling()