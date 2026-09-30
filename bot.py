
import os
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from urllib.parse import urlencode

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

API = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# TELEGRAM API
# =========================

def telegram(method, data=None):
    url = f"{API}/{method}"

    if data is None:
        data = {}

    body = urlencode(data).encode("utf-8")

    request = Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    with urlopen(request, timeout=70) as response:
        return json.loads(response.read().decode("utf-8"))


def send_message(chat_id, text):
    return telegram(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text
        }
    )


# =========================
# BUYRUQLAR
# =========================

def handle_message(message):

    chat = message.get("chat", {})
    chat_id = chat.get("id")

    if not chat_id:
        return

    text = message.get("text", "")

    if text == "/start":
        send_message(
            chat_id,
            "Assalomu alaykum! 👋\n\n"
            "RS online bot ishga tushdi ✅\n\n"
            "Buyruqlar:\n"
            "/start — botni ishga tushirish\n"
            "/help — yordam\n"
            "/status — bot holati"
        )

    elif text == "/help":
        send_message(
            chat_id,
            "Yordam 🛠\n\n"
            "/start — boshlash\n"
            "/status — bot holatini tekshirish"
        )

    elif text == "/status":
        send_message(
            chat_id,
            "Bot ishlayapti ✅\n"
            "Server: Render\n"
            "Telegram ulanishi: OK"
        )

    else:
        send_message(
            chat_id,
            "Xabaringiz qabul qilindi ✅\n\n"
            f"Siz yozdingiz: {text}"
        )


# =========================
# POLLING
# =========================

def run_bot():

    print("Bot ishga tushmoqda...")

    # Eski webhookni o'chirish
    try:
        result = telegram(
            "deleteWebhook",
            {
                "drop_pending_updates": "false"
            }
        )

        print("Webhook:", result)

    except Exception as e:
        print("Webhook xatosi:", e)

    # Bot ma'lumotini tekshirish
    try:
        result = telegram("getMe")
        print("BOT:", result)
    except Exception as e:
        print("TOKEN xatosi:", e)
        return

    offset = 0

    print("Telegram polling boshlandi...")

    while True:

        try:

            result = telegram(
                "getUpdates",
                {
                    "offset": offset,
                    "timeout": 50
                }
            )

            if not result.get("ok"):
                print("Telegram xatosi:", result)
                time.sleep(3)
                continue

            updates = result.get("result", [])

            for update in updates:

                offset = update["update_id"] + 1

                try:

                    message = update.get("message")

                    if message:
                        handle_message(message)

                except Exception as e:
                    print("Xabar xatosi:", e)

        except Exception as e:

            print("Polling xatosi:", e)
            time.sleep(5)


# =========================
# RENDER SERVER
# =========================

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

    def log_message(self, format, *args):
        return


def run_server():

    port = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    print(f"Web server port: {port}")

    server.serve_forever()


# =========================
# START
# =========================

if __name__ == "__main__":

    server_thread = threading.Thread(
        target=run_server,
        daemon=True
    )

    server_thread.start()

    run_bot()