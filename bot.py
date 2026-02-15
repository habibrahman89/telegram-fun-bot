import os
from telegram.ext import Application

from config import BOT_TOKEN

from handlers import admin, fun, quiz, welcome, music

from services.cleanup import cleanup_music_folder
from services.database import init_db


async def error_handler(update, context):
    print("❌ Error:", context.error)


def main():
    # 🔥 Initialize database FIRST
    init_db()

    # 🔥 Build app
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(60)
        .write_timeout(180)
        .build()
    )

    # 🔥 Register handlers
    admin.register(app)
    fun.register(app)
    quiz.register(app)
    welcome.register(app)
    music.register(app)

    # 🔥 Error handler
    app.add_error_handler(error_handler)

    # 🔥 Cleanup music folder
    music_dir = os.path.join(os.path.dirname(__file__), "music")
    cleanup_music_folder(music_dir)

    print("🤖 Bot is running...")

    # 🔥 Start bot (ONLY ONCE)
    app.run_polling()


if __name__ == "__main__":
    main()