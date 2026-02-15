import random
from telegram.ext import CommandHandler
from services.quiz_data import QUESTIONS

async def quiz(update, context):
    q = random.choice(QUESTIONS)
    context.chat_data["answer"] = q["correct"]

    options = "\n".join(
        f"{i+1}. {opt}" for i, opt in enumerate(q["a"])
    )

    await update.message.reply_text(
        f"🧠 {q['q']}\n\n{options}\n\nReply with /ans <number>"
    )

async def ans(update, context):
    try:
        user_ans = int(context.args[0]) - 1
    except:
        await update.message.reply_text("Usage: /ans 1")
        return

    if user_ans == context.chat_data.get("answer"):
        await update.message.reply_text("✅ Correct!")
    else:
        await update.message.reply_text("❌ Wrong!")

def register(app):
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("ans", ans))