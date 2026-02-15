from telegram.ext import CommandHandler
import random

JOKES = [
    "Why don’t programmers like nature? Too many bugs.",
    "I told my computer I needed a break. It froze.",
]

async def joke(update, context):
    await update.message.reply_text(random.choice(JOKES))

def register(app):
    app.add_handler(CommandHandler("joke", joke))