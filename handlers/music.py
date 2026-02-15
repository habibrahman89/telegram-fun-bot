import os
import asyncio
from services.users import increment_play, save_user
from services.users import save_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from yt_dlp import YoutubeDL
from services.cleanup import cleanup_music_folder

from services.db_queue import (
    add_db_queue,
    pop_db_queue,
    list_db_queue,
    clear_db_queue
)

from collections import deque

# -----------------------
# MUSIC QUEUE SYSTEM
# -----------------------

MUSIC_QUEUES = {}      # chat_id -> deque
NOW_PLAYING = set()   # currently playing chats


def add_to_queue(chat_id, item):
    if chat_id not in MUSIC_QUEUES:
        MUSIC_QUEUES[chat_id] = deque()

    MUSIC_QUEUES[chat_id].append(item)


def pop_from_queue(chat_id):
    if chat_id not in MUSIC_QUEUES:
        return None

    if not MUSIC_QUEUES[chat_id]:
        return None

    return MUSIC_QUEUES[chat_id].popleft()


def list_queue(chat_id):
    if chat_id not in MUSIC_QUEUES:
        return []

    return list(MUSIC_QUEUES[chat_id])


def clear_queue(chat_id):
    MUSIC_QUEUES.pop(chat_id, None)
    NOW_PLAYING.discard(chat_id)


def is_playing(chat_id):
    return chat_id in NOW_PLAYING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "music")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
    "quiet": True,
    "nocheckcertificate": True,
    "geo_bypass": True,

    "ffmpeg_location": r"C:\ffmpeg\bin",

    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),

    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "128",
    }],
}

# ------------------------
# BUTTON & MENUS FUNCTION
# ------------------------
def music_controls():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏭ Skip", callback_data="music_skip"),
            InlineKeyboardButton("📜 Queue", callback_data="music_queue"),
        ],
        [
            InlineKeyboardButton("⏹ Stop", callback_data="music_stop"),
        ]
    ])


async def music_buttons(update, context):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    action = query.data

    if action == "music_skip":
        await query.edit_message_caption(
            caption="⏭ Skipped",
            reply_markup=music_controls()
        )
        await send_next_song(update, context)

    elif action == "music_queue":
        q = list_queue(chat_id)
        if not q:
            await query.message.reply_text("📭 Queue empty")
        else:
            text = "\n".join(
                f"{i+1}. {os.path.basename(s)}" for i, s in enumerate(q)
            )
            await query.message.reply_text(f"🎶 Queue:\n{text}")

    elif action == "music_stop":
        clear_queue(chat_id)
        await query.edit_message_caption(
            caption="⏹ Music stopped",
            reply_markup=None
        )


# ------------------------
# CORE DOWNLOAD FUNCTION
# ------------------------
def download_song(query):
    with YoutubeDL(ydl_opts) as ydl:
        if query.startswith("http"):
            info = ydl.extract_info(query, download=True)
        else:
            info = ydl.extract_info(
                f"ytsearch1:{query}", download=True
            )["entries"][0]

        return os.path.join(DOWNLOAD_DIR, f"{info['id']}.mp3")

# ------------------------
# /play → SEND + QUEUE
# ------------------------
async def play(update, context):

    user = update.effective_user

    save_user(user)
    increment_play(user.id)

    if not context.args:
        await update.message.reply_text("Usage: /play <song>")
        return

    chat_id = update.effective_chat.id
    query = " ".join(context.args)

    add_to_queue(chat_id, query)

    await update.message.reply_text(f"➕ Added: {query}")

    if not is_playing(chat_id):
        await send_next_song(update, context)

# ------------------------
# SEND NEXT SONG
# ------------------------
async def send_next_song(update, context):
    chat_id = update.effective_chat.id

    query = pop_from_queue(chat_id)

    if not query:
        NOW_PLAYING.discard(chat_id)
        return

    NOW_PLAYING.add(chat_id)

    loop = asyncio.get_event_loop()

    try:
        song_path = await loop.run_in_executor(
            None, download_song, query
        )

        with open(song_path, "rb") as f:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=f,
                caption=f"▶️ Now Playing: {query}",
                reply_markup=music_controls()
            )

        os.remove(song_path)

    except Exception as e:
        print("PLAY ERROR:", e)
        await send_next_song(update, context)

# ------------------------
# /download → MP3 ONLY
# ------------------------
async def download(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /download <song or YouTube link>")
        return

    query = " ".join(context.args)
    await update.message.reply_text("⬇️ Downloading MP3...")

    loop = asyncio.get_event_loop()

    try:
        song = await loop.run_in_executor(None, download_song, query)
    except Exception as e:
        await update.message.reply_text(
            "❌ Unable to download this video.\n"
            "It may be blocked, private, or restricted."
        )
        print("DOWNLOAD ERROR:", e)
        return

    try:
        with open(song, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=os.path.basename(song),
                caption="⬇️ Download complete"
            )
        os.remove(song)

        cleanup_music_folder(DOWNLOAD_DIR)

    except Exception as e:
        print("SEND ERROR:", e)
        await update.message.reply_text("❌ Failed to send file")

# ------------------------
# QUEUE COMMANDS
# ------------------------
async def skip(update, context):
    await send_next_song(update, context)

async def queue(update, context):
    q = list_queue(update.effective_chat.id)

    if not q:
        await update.message.reply_text("📭 Queue empty")
        return

    text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(q))

    await update.message.reply_text("🎶 Queue:\n" + text)

async def stop(update, context):
    clear_queue(update.effective_chat.id)
    await update.message.reply_text("⏹ Queue cleared")


async def profile(update, context):
    from services.database import get_connection

    user = update.effective_user

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT plays FROM users WHERE user_id = ?
    """, (user.id,))

    row = cur.fetchone()
    conn.close()

    plays = row[0] if row else 0

    await update.message.reply_text(
        f"👤 Profile\n\n"
        f"Name: {user.first_name}\n"
        f"Plays: {plays}"
    )

# REGISTER HANDLERS
# ------------------------
def register(app):
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("download", download))
    app.add_handler(CommandHandler("skip", skip))
    app.add_handler(CommandHandler("queue", queue))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("profile", profile))


    # 🔥 INLINE BUTTON HANDLER
    app.add_handler(CallbackQueryHandler(music_buttons, pattern="^music_"))