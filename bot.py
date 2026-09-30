import os
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# =========================
# SOZLAMALAR
# =========================

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
        request = Request(url, method="POST")
    else:
        body = json.dumps(data).encode("utf-8")
        request = Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

    try:
        with urlopen(request, timeout=65) as response:
            return json.loads(response.read().decode("utf-8"))

    except HTTPError as e:
        print("Telegram HTTP xatosi:", e)
        return None

    except URLError as e:
        print("Internet xatosi:", e)
        return None

    except Exception as e:
        print("Telegram xatosi:", e)
        return None


# =========================
# XABAR YUBORISH
# =========================

def send_message(chat_id, text):
    return telegram(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text
        }
    )


# =========================
# XABARLARNI QAYTA ISHLASH
# =========================

def handle_message(message):
    chat = message.get("chat", {})
    chat_id = chat.get("id")

    if not chat_id:
        return

    text = message.get("text", "")
    text = text.strip()

    if text == "/start":
        send_message(
            chat_id,
            "Salom! 👋\n\n"
            "RS online bot ishga tushdi ✅\n\n"
            "Buyruqlar:\n"
            "/start - botni ishga tushirish\n"
            "/help - yordam\n"
            "/id - Telegram ID"
        )
        return

    if text == "/help":
        send_message(
            chat_id,
            "Bot ishlayapti ✅\n\n"
            "Hozircha oddiy rejimda.\n"
            "Keyingi bosqichda kerakli funksiyalar qo‘shiladi."
        )
        return

    if text == "/id":
        send_message(
            chat_id,
            f"Sizning Telegram ID: {chat_id}"
        )
        return

    if text:
        send_message(
            chat_id,
            f"Xabaringiz qabul qilindi ✅\n\n{text}"
        )


# =========================
# TELEGRAM POLLING
# =========================

def run_bot():

    print("Bot ishga tushmoqda...")

    # Eski webhookni o‘chirish
    result = telegram("deleteWebhook")

    print("Webhook:", result)

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

            if not result:
                time.sleep(3)
                continue

            if not result.get("ok"):
                print("Telegram API xatosi:", result)
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
                        print("Yangi xabar:", message)
                        handle_message(message)

                except Exception as e:
                    print("Xabarni qayta ishlash xatosi:", e)

        except Exception as e:
            print("Polling xatosi:", e)
            time.sleep(5)


# =========================
# RENDER WEB SERVER
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