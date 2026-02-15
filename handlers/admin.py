from telegram.ext import CommandHandler
from utils.permissions import admin_only

@admin_only
async def ban(update, context):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to ban.")
        return

    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"🚫 {user.first_name} banned")

def register(app):
    app.add_handler(CommandHandler("ban", ban))