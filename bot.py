import os
import json
import time
import urllib.request
import urllib.parse
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==============================
# SOZLAMALAR
# ==============================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

API = f"https://api.telegram.org/bot{TOKEN}"

# ==============================
# TELEGRAM API
# ==============================

def telegram(method, data=None):
    data = data or {}

    encoded = urllib.parse.urlencode(data).encode()

    request = urllib.request.Request(
        f"{API}/{method}",
        data=encoded,
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=40) as response:
        return json.loads(response.read().decode())


# ==============================
# WEBHOOKNI O'CHIRISH
# ==============================

def prepare_bot():
    try:
        result = telegram(
            "deleteWebhook",
            {"drop_pending_updates": False}
        )

        print("Webhook holati:", result)

    except Exception as e:
        print("Webhook xatosi:", e)


# ==============================
# XABAR YUBORISH
# ==============================

def send_message(chat_id, text):
    try:
        result = telegram(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text
            }
        )

        print("Xabar yuborildi:", result)

    except Exception as e:
        print("Xabar yuborishda xato:", e)


# ==============================
# BOT ISHI
# ==============================

def bot_loop():

    prepare_bot()

    offset = 0

    print("Telegram bot ishga tushdi!")

    while True:

        try:

            result = telegram(
                "getUpdates",
                {
                    "offset": offset,
                    "timeout": 25,
                    "allowed_updates": json.dumps(["message"])
                }
            )

            if not result.get("ok"):
                print("Telegram API xatosi:", result)
                time.sleep(5)
                continue

            updates = result.get("result", [])

            for update in updates:

                # keyingi update uchun offset
                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                chat = message.get("chat")

                if not chat:
                    continue

                chat_id = chat.get("id")

                text = message.get("text", "").strip()

                print(
                    "Xabar:",
                    chat_id,
                    text
                )

                # ==========================
                # /start
                # ==========================

                if text == "/start":

                    send_message(
                        chat_id,
                        "Salom! RS online bot ishlayapti ✅\n\n"
                        "Bot sizning xabarlaringizni qabul qildi."
                    )

                # ==========================
                # /help
                # ==========================

                elif text == "/help":

                    send_message(
                        chat_id,
                        "Buyruqlar:\n\n"
                        "/start - Botni ishga tushirish\n"
                        "/help - Yordam"
                    )

                # ==========================
                # BOSHQA XABARLAR
                # ==========================

                else:

                    send_message(
                        chat_id,
                        "Xabaringiz qabul qilindi ✅\n\n"
                        f"Siz yozdingiz: {text}"
                    )

        except Exception as e:

            print("Bot xatosi:", e)

            time.sleep(5)


# ==============================
# RENDER SERVER
# ==============================

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )

        self.end_headers()

        self.wfile.write(
            b"RS online bot ishlayapti!"
        )

    def log_message(self, format, *args):
        return


# ==============================
# MAIN
# ==============================

def main():

    # Telegram botni alohida threadda ishga tushirish
    thread = threading.Thread(
        target=bot_loop,
        daemon=True
    )

    thread.start()

    # Render porti
    port = int(
        os.getenv("PORT", "10000")
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    print(
        f"Render server ishga tushdi: {port}"
    )

    server.serve_forever()


# ==============================
# START
# ==============================

if __name__ == "__main__":
    main()