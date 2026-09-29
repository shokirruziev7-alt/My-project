import os
import json
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

    API = f"https://api.telegram.org/bot{TOKEN}"


    def telegram(method, data=None):
        data = data or {}
            encoded = urllib.parse.urlencode(data).encode()
                request = urllib.request.Request(
                        f"{API}/{method}",
                                data=encoded
                                    )
                                        with urllib.request.urlopen(request, timeout=30) as response:
                                                return json.loads(response.read())


                                                def send_message(chat_id, text):
                                                    telegram("sendMessage", {
                                                            "chat_id": chat_id,
                                                                    "text": text
                                                                        })


                                                                        def set_webhook():
                                                                            url = os.getenv("RENDER_EXTERNAL_URL")
                                                                                if url:
                                                                                        telegram("setWebhook", {"url": url})


                                                                                        class Handler(BaseHTTPRequestHandler):

                                                                                            def do_GET(self):
                                                                                                    self.send_response(200)
                                                                                                            self.end_headers()
                                                                                                                    self.wfile.write(b"Bot is running")

                                                                                                                        def do_POST(self):
                                                                                                                                length = int(self.headers.get("Content-Length", 0))
                                                                                                                                        body = self.rfile.read(length)

                                                                                                                                                try:
                                                                                                                                                            update = json.loads(body)
                                                                                                                                                                        message = update.get("message", {})
                                                                                                                                                                                    chat = message.get("chat", {})
                                                                                                                                                                                                text = message.get("text", "")

                                                                                                                                                                                                            if chat:
                                                                                                                                                                                                                            if text == "/start":
                                                                                                                                                                                                                                                send_message(
                                                                                                                                                                                                                                                                        chat["id"],
                                                                                                                                                                                                                                                                                                "Salom! Bot ishlayapti. 🤖"
                                                                                                                                                                                                                                                                                                                    )

                                                                                                                                                                                                                                                                                                                                    elif text == "/help":
                                                                                                                                                                                                                                                                                                                                                        send_message(
                                                                                                                                                                                                                                                                                                                                                                                chat["id"],
                                                                                                                                                                                                                                                                                                                                                                                                        "Bu Telegram bot."
                                                                                                                                                                                                                                                                                                                                                                                                                            )

                                                                                                                                                                                                                                                                                                                                                                                                                                            else:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                send_message(
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        chat["id"],
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                f"Siz yozdingiz: {text}"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    )

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            except Exception as e:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        print("ERROR:", e)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                self.send_response(200)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        self.end_headers()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                self.wfile.write(b"OK")

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    def log_message(self, format, *args):
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            pass


                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            port = int(os.environ.get("PORT", "10000"))

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            set_webhook()

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            server = HTTPServer(("0.0.0.0", port), Handler)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            print(f"Server running on port {port}")

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            server.serve_forever()