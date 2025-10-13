from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ApplicationBuilder, InlineQueryHandler, ContextTypes
import random, uuid, os

# Берём токен из переменной окружения
TOKEN = os.environ.get("TOKEN")

async def inline_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return

    try:
        max_num = int(query)
        if max_num < 1:
            return

        # Генерируем число только для отправки сообщения
        result = random.randint(1, max_num)
        text = f"🎲 Выпало: {result} из {max_num}"

        # Inline результат
        await update.inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="🎲 Генерировать число",             # текст в сниппете
                    description="Нажми, чтобы узнать число",  # описание в сниппете
                    input_message_content=InputTextMessageContent(text),
                    thumb_url="https://cdn-icons-png.flaticon.com/512/4100/4100836.png"  # картинка в превью
                )
            ],
            cache_time=0  # всегда свежий результат
        )

    except ValueError:
        await update.inline_query.answer(
            results=[],
            switch_pm_text="Введите число, например: 100",
            switch_pm_parameter="start"
        )

# Создаём приложение и добавляем обработчик inline-запросов
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(InlineQueryHandler(inline_roll))

# Запускаем бота
app.run_polling()
