import os
import json
import time
import urllib.request
import urllib.parse
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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


def send_message(chat_id, text):
    telegram("sendMessage", {
        "chat_id": chat_id,
        "text": text
    })


def bot_loop():
    offset = 0

    print("Telegram bot ishga tushdi!")

    while True:
        try:
            result = telegram("getUpdates", {
                "offset": offset,
                "timeout": 25
            })

            for update in result.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(
                        chat_id,
                        "Salom! RS online bot ishlayapti ✅"
                    )
                else:
                    send_message(
                        chat_id,
                        "Xabaringiz qabul qilindi ✅"
                    )

        except Exception as e:
            print("Bot xatosi:", e)
            time.sleep(5)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"RS online bot ishlayapti!")

    def log_message(self, format, *args):
        return


def main():
    thread = threading.Thread(
        target=bot_loop,
        daemon=True
    )
    thread.start()

    port = int(os.getenv("PORT", "10000"))

    server = HTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    print(f"Server ishga tushdi: {port}")
    server.serve_forever()


if __name__ == "__main__":
    main()