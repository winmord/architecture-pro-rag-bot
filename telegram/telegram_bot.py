import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


BOT_TOKEN = os.getenv("BOT_TOKEN")

RAG_URL = os.getenv("RAG_URL", "http://localhost:8000/ask")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Задай вопрос")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    try:
        response = requests.post(
            RAG_URL,
            json={"query": question},
            timeout=60
        )

        if response.status_code != 200:
            await update.message.reply_text("Ошибка RAG сервера")
            return

        answer = response.json().get("answer", "I don't know")

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()