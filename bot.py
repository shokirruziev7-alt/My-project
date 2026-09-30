import os
import json
import time
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

API = f"https://api.telegram.org/bot{TOKEN}"


def telegram(method, data=None):
    data = data or {}
    encoded = urllib.parse.urlencode(data).encode()

    req = urllib.request.Request(
        f"{API}/{method}",
        data=encoded
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode())


def send(chat_id, text):
    telegram("sendMessage", {
        "chat_id": chat_id,
        "text": text
    })


def bot_loop():
    # Eski webhook bo‘lsa o‘chiradi
    telegram("deleteWebhook")

    offset = 0

    while True:
        try:
            result = telegram("getUpdates", {
                "offset": offset,
                "timeout": 25
            })

            for update in result.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message", {})
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = message.get("text", "")

                if not chat_id:
                    continue

                if text == "/start":
                    send(
                        chat_id,
                        "Salom! 👋\n\n"
                        "RS online bot ishga tushdi.\n"
                        "Buyruq yuboring."
                    )

                elif text == "/help":
                    send(
                        chat_id,
                        "Buyruqlar:\n"
                        "/start - botni boshlash\n"
                        "/help - yordam"
                    )

                else:
                    send(
                        chat_id,
                        "Xabaringiz qabul qilindi: " + text
                    )

        except Exception as e:
            print("Xatolik:", e)
            time.sleep(5)


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")

    def log_message(self, format, *args):
        return


def main():
    thread = threading.Thread(target=bot_loop, daemon=True)
    thread.start()

    port = int(os.getenv("PORT", "10000"))

    server = HTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    print("Bot ishga tushdi...")
    server.serve_forever()


if __name__ == "__main__":
    main()