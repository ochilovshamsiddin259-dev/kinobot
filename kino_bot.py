import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TOKEN_HERE")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

movies = {
    "uzbek": [
        {"id": "u1", "name": "O'g'il ona", "year": 2023, "file_id": None, "desc": "O'zbek filmi"},
        {"id": "u2", "name": "Muhabbat Yo'li", "year": 2022, "file_id": None, "desc": "O'zbek romantik filmi"},
    ],
    "turk": [
        {"id": "t1", "name": "Dirilis Ertugrul", "year": 2014, "file_id": None, "desc": "Turk tarixiy serial"},
        {"id": "t2", "name": "Qora Qush", "year": 2022, "file_id": None, "desc": "Turk detektiv serial"},
    ],
    "korea": [
        {"id": "k1", "name": "Squid Game", "year": 2021, "file_id": None, "desc": "Koreya thriller serial"},
        {"id": "k2", "name": "Crash Landing on You", "year": 2019, "file_id": None, "desc": "Koreya romantik serial"},
    ]
}

REKLAMA = """
━━━━━━━━━━━━━━━
📢 REKLAMA
🏪 Sizning reklamangiz shu yerda bo'lishi mumkin!
📩 @admin ga yozing
━━━━━━━━━━━━━━━
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek kinolar", callback_data="cat_uzbek"),
            InlineKeyboardButton("🇹🇷 Turk kinolar", callback_data="cat_turk"),
        ],
        [InlineKeyboardButton("🇰🇷 Koreya kinolar", callback_data="cat_korea")],
        [
            InlineKeyboardButton("🔍 Qidirish", callback_data="search"),
            InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        ]
    ]
    await update.message.reply_text(
        "🎬 *KinoOlami Bot ga xush kelibsiz!*\n\n"
        "O'zbek, Turk va Koreya kinolarini bepul tomosha qiling!\n\n"
        "👇 Kategoriya tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("cat_", "")
    cat_names = {"uzbek": "🇺🇿 O'zbek kinolar", "turk": "🇹🇷 Turk kinolar", "korea": "🇰🇷 Koreya kinolar"}
    film_list = movies.get(cat, [])
    keyboard = []
    for film in film_list:
        keyboard.append([InlineKeyboardButton(
            f"🎬 {film['name']} ({film['year']})",
            callback_data=f"film_{cat}_{film['id']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")])
    await query.edit_message_text(
        f"*{cat_names[cat]}*\n\nFilm tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_film(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    cat = parts[1]
    film_id = parts[2]
    film = next((f for f in movies[cat] if f["id"] == film_id), None)
    if not film:
        await query.edit_message_text("Film topilmadi.")
        return
    keyboard = [
        [InlineKeyboardButton("▶️ Tomosha qilish", callback_data=f"watch_{cat}_{film_id}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data=f"cat_{cat}")]
    ]
    await query.edit_message_text(
        f"🎬 *{film['name']}*\n"
        f"📅 Yil: {film['year']}\n"
        f"📝 {film['desc']}\n\n"
        f"▶️ Ko'rish uchun tugmani bosing:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def watch_film(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    cat = parts[1]
    film_id = parts[2]
    film = next((f for f in movies[cat] if f["id"] == film_id), None)
    await query.edit_message_text(REKLAMA, parse_mode="Markdown")
    if film and film["file_id"]:
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=film["file_id"],
            caption=f"🎬 *{film['name']}*\n\n@KinoOlami202595Bot",
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"⏳ *{film['name']}* tez orada qo'shiladi!\n\nAdmin: @Shams0695",
            parse_mode="Markdown"
        )

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek kinolar", callback_data="cat_uzbek"),
            InlineKeyboardButton("🇹🇷 Turk kinolar", callback_data="cat_turk"),
        ],
        [InlineKeyboardButton("🇰🇷 Koreya kinolar", callback_data="cat_korea")],
        [
            InlineKeyboardButton("🔍 Qidirish", callback_data="search"),
            InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        ]
    ]
    await query.edit_message_text(
        "🎬 *KinoOlami Bot*\n\n👇 Kategoriya tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["searching"] = True
    await query.edit_message_text(
        "🔍 *Qidirish*\n\nFilm nomini yozing:",
        parse_mode="Markdown"
    )

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("searching"):
        return
    context.user_data["searching"] = False
    q = update.message.text.lower()
    results = []
    for cat, films in movies.items():
        for film in films:
            if q in film["name"].lower():
                results.append((cat, film))
    if not results:
        await update.message.reply_text("❌ Film topilmadi. Boshqa nom kiriting.")
        return
    keyboard = []
    for cat, film in results:
        keyboard.append([InlineKeyboardButton(
            f"🎬 {film['name']} ({film['year']})",
            callback_data=f"film_{cat}_{film['id']}"
        )])
    keyboard.append([InlineKeyboardButton("🏠 Bosh sahifa", callback_data="back_main")])
    await update.message.reply_text(
        f"🔍 *'{update.message.text}'* bo'yicha natijalar:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    total = sum(len(v) for v in movies.values())
    await query.edit_message_text(
        f"📊 *Statistika*\n\n"
        f"🇺🇿 O'zbek filmlar: {len(movies['uzbek'])} ta\n"
        f"🇹🇷 Turk filmlar: {len(movies['turk'])} ta\n"
        f"🇰🇷 Koreya filmlar: {len(movies['korea'])} ta\n"
        f"━━━━━━━━━━━━\n"
        f"🎬 Jami: {total} ta film",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]])
    )

async def admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "➕ *Film qo'shish:*\n\n"
        "Film faylini yuboring, caption da:\n"
        "`uzbek|Film Nomi|2024|Tavsif`\n\n"
        "Kategoriyalar: `uzbek`, `turk`, `korea`",
        parse_mode="Markdown"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not update.message.caption:
        return
    try:
        parts = update.message.caption.split("|")
        cat, name, year, desc = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        file_id = update.message.video.file_id
        new_id = f"{cat[0]}{len(movies[cat])+1}"
        movies[cat].append({"id": new_id, "name": name, "year": int(year), "file_id": file_id, "desc": desc})
        await update.message.reply_text(f"✅ '{name}' filmi qo'shildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}\n\nFormat: `kategoriya|nom|yil|tavsif`", parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", admin_add))
    app.add_handler(CallbackQueryHandler(show_category, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(show_film, pattern="^film_"))
    app.add_handler(CallbackQueryHandler(watch_film, pattern="^watch_"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(search_prompt, pattern="^search$"))
    app.add_handler(CallbackQueryHandler(stats, pattern="^stats$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    logger.info("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
