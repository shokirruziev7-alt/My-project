import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Loglar
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Telegram token
TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\n\n"
        "Bot muvaffaqiyatli ishlayapti.\n\n"
        "Buyruqlar:\n"
        "/start — botni boshlash\n"
        "/help — yordam\n"
        "/about — bot haqida"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Yordam\n\n"
        "Menga oddiy xabar yuboring — men javob beraman.\n\n"
        "Buyruqlar:\n"
        "/start\n"
        "/help\n"
        "/about"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bu Telegram bot.\n"
        "Bot server orqali 24/7 ishlashi uchun yaratilgan."
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        text = update.message.text

        await update.message.reply_text(
            f"✅ Xabaringiz keldi!\n\n"
            f"Siz yozdingiz:\n{text}"
        )


def main():
    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. Render Environment Variables "
            "ichiga BOT_TOKEN qo‘shing."
        )

    app = Application.builder().token(TOKEN).build()

    # Buyruqlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))

    # Oddiy xabarlar
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    print("🤖 Bot ishga tushdi...")
    
    # Telegramdan xabarlarni doimiy kutadi
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()