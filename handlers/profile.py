async def profile(update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"👤 {user.first_name}\n"
        f"ID: {user.id}\n"
        f"Level: 3\nXP: 120"
    )

def register(app):
    app.add_handler(CommandHandler("profile", profile))