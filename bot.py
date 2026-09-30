import os
import json
import time
import threading
import urllib.request
import urllib.parse
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
    url = f"{API}/{method}"

    if data is None:
        data = {}

    encoded = urllib.parse.urlencode(data).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=encoded,
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=40) as response:
        return json.loads(response.read().decode("utf-8"))


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

        if not result.get("ok"):
            print("sendMessage xatosi:", result)

    except Exception as e:
        print("Xabar yuborishda xato:", e)


# ==============================
# BUYRUQLAR
# ==============================

def process_message(message):

    if not message:
        return

    chat = message.get("chat")

    if not chat:
        return

    chat_id = chat.get("id")

    text = message.get("text", "").strip()

    if text == "/start":

        send_message(
            chat_id,
            "Salom! RS online bot ishlayapti ✅\n\n"
            "Bot Telegram xabarlarini qabul qilmoqda."
        )

    elif text == "/help":

        send_message(
            chat_id,
            "Yordam:\n\n"
            "/start — botni ishga tushirish\n"
            "/help — yordam"
        )

    elif text:

        send_message(
            chat_id,
            f"Xabaringiz qabul qilindi ✅\n\n{text}"
        )


# ==============================
# TELEGRAM POLLING
# ==============================

def bot_loop():

    offset = 0

    print("================================")
    print("Telegram bot ishga tushmoqda...")
    print("================================")

    # Eski webhook bo'lsa olib tashlaymiz
    try:
        telegram("deleteWebhook", {"drop_pending_updates": "false"})
        print("Webhook tozalandi.")
    except Exception as e:
        print("Webhook tozalash xatosi:", e)

    # Botni tekshiramiz
    try:
        me = telegram("getMe")

        if me.get("ok"):
            bot = me["result"]
            print(
                "BOT:",
                bot.get("first_name"),
                "@"+bot.get("username", "")
            )
        else:
            print("getMe xatosi:", me)

    except Exception as e:
        print("Telegram ulanish xatosi:", e)

    print("Polling boshlandi...")

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
                print("getUpdates xatosi:", result)
                time.sleep(5)
                continue

            updates = result.get("result", [])

            for update in updates:

                update_id = update.get("update_id")

                if update_id is not None:
                    offset = update_id + 1

                try:
                    message = update.get("message")

                    if message:
                        print(
                            "Yangi xabar:",
                            message.get("text", "")
                        )

                        process_message(message)

                except Exception as e:
                    print("Xabarni qayta ishlash xatosi:", e)

        except Exception as e:

            print("Polling xatosi:", e)

            time.sleep(5)


# ==============================
# RENDER HEALTH SERVER
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
            b"RS online bot ishlayapti"
        )

    def do_HEAD(self):

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain"
        )

        self.end_headers()

    def log_message(self, format, *args):
        return


# ==============================
# MAIN
# ==============================

def main():

    # Telegram botni alohida threadda ishga tushiramiz
    bot_thread = threading.Thread(
        target=bot_loop,
        daemon=True
    )

    bot_thread.start()

    # Render porti
    port = int(
        os.getenv("PORT", "10000")
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    print("================================")
    print(f"Render server ishga tushdi: {port}")
    print("RS online bot tayyor.")
    print("================================")

    server.serve_forever()


if __name__ == "__main__":
    main()