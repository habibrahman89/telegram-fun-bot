from telegram import ChatMember
from telegram.ext import ChatMemberHandler
from utils.images import generate_welcome_image

async def welcome(update, context):

    from services.database import save_user

    for user in update.message.new_chat_members:
        save_user(user)

    chat_member = update.chat_member

    print("WELCOME EVENT FIRED")
    print(chat_member.old_chat_member.status, "→", chat_member.new_chat_member.status)

    # Trigger only when a NEW user joins
    if chat_member.old_chat_member.status in ("left", "kicked") and \
       chat_member.new_chat_member.status == "member":

        user = chat_member.new_chat_member.user

        img = generate_welcome_image(user)
        await context.bot.send_photo(
            chat_id=chat_member.chat.id,
            photo=open(img, "rb"),
            caption=f"👋 Welcome {user.first_name}!"
        )

def register(app):
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))
