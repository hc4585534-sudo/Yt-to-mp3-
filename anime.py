import os
import asyncio
import random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")  # Railway env variable

# 🎬 Intro Effect
async def intro(message):
    steps = [
        "⚡ Booting system...",
        "⚡ Connecting to network...",
        "⚡ Bypassing security...",
        "💀 Hacker Mode Activated"
    ]
    msg = await message.reply_text("🚀 Starting...")
    for step in steps:
        await asyncio.sleep(1)
        await msg.edit_text(step)
    return msg

# 📊 Progress Bar
async def progress(message, text="Processing"):
    msg = await message.reply_text("⚡ Initializing...")
    for i in range(0, 101, 10):
        bar = "█"*(i//10) + "░"*(10-i//10)
        await asyncio.sleep(random.uniform(0.4,0.8))
        await msg.edit_text(f"{text}\n[{bar}] {i}%")
    return msg

# 🎯 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💀 Send link to begin")

# 🔗 LINK HANDLE
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("❌ Valid link bhejo")
        return

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("🎬 Video", callback_data="video"),
            InlineKeyboardButton("🎧 MP3", callback_data="mp3")
        ]
    ]

    await update.message.reply_text(
        "💀 Select operation mode:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔘 BUTTON
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")

    if not url:
        await query.message.reply_text("❌ Link missing")
        return

    mode = query.data

    await intro(query.message)
    await progress(query.message, "🔓 Accessing server")

    # 🌐 COMMON OPTIONS
    ydl_base = {
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        "cookiefile": "cookies.txt",
        "no_check_certificate": True,
        "geo_bypass": True,
        "http_headers": {
        "User-Agent": "Mozilla/5.0"
          },# 🔥 IMPORTANT
        "extractor_args": {
           "youtube": {
              "skip": ["hls", "dash"]
           }
        }
    }

    # 🎬 VIDEO
    if mode == "video":
        ydl_opts = {
          **ydl_base,
          'format': 'best',
          'noplaylist': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            if not os.path.exists(filename):
                await query.message.reply_text("❌ Download failed")
                return

            await progress(query.message, "📂 Extracting video")

            with open(filename, "rb") as f:
                await query.message.reply_video(f)

            os.remove(filename)

        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")

    # 🎧 MP3
    elif mode == "mp3":
        ydl_opts = {
            **ydl_base,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                mp3 = filename.rsplit(".",1)[0] + ".mp3"

            if not os.path.exists(mp3):
                await query.message.reply_text("❌ MP3 failed")
                return

            await progress(query.message, "🎧 Extracting audio")

            with open(mp3, "rb") as f:
                await query.message.reply_audio(f)

            os.remove(mp3)

        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")

    await query.message.reply_text(
        "💀 MISSION COMPLETE\n⚡ File extracted successfully"
    )

# 🚀 MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button))

    print("💀 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
