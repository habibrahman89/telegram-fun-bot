from functools import wraps

def admin_only(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        member = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
        )
        if member.status not in ("administrator", "creator"):
            await update.message.reply_text("Admins only.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper