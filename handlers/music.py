import os
import asyncio
from collections import deque

from yt_dlp import YoutubeDL

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from services.users import increment_play, save_user
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

def get_stream_url(query):
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "skip_download": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        if query.startswith("http"):
            info = ydl.extract_info(query, download=False)
        else:
            info = ydl.extract_info(
                f"ytsearch1:{query}", download=False
            )["entries"][0]

        return info["url"]

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
                f"{i+1}. {s}" for i, s in enumerate(q)
            )
            await query.message.reply_text(f"🎶 Queue:\n{text}")

    elif action == "music_stop":
        clear_queue(chat_id)
        await query.edit_message_caption(
            caption="⏹ Music stopped",
            reply_markup=None
        )

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

    # Reset playing state
    NOW_PLAYING.discard(chat_id)

    query = pop_from_queue(chat_id)

    if not query:
        return

    NOW_PLAYING.add(chat_id)

    loop = asyncio.get_event_loop()

    try:
        url = await loop.run_in_executor(
            None, get_stream_url, query
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"▶️ Now Playing: {query}\n\n🎧 {url}",
            reply_markup=music_controls()
        )

    except Exception as e:
        print("PLAY ERROR:", e)
        await send_next_song(update, context)

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

def register(app):
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("skip", skip))
    app.add_handler(CommandHandler("queue", queue))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("profile", profile))

    app.add_handler(CallbackQueryHandler(music_buttons, pattern="^music_"))
