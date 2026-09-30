import os
import json
import time
import urllib.request
import urllib.parse
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


# ==========================================
# SOZLAMALAR
# ==========================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")


API = f"https://api.telegram.org/bot{TOKEN}"


# ==========================================
# TELEGRAM API
# ==========================================

def telegram(method, data=None):

    if data is None:
        data = {}

    encoded = urllib.parse.urlencode(data).encode("utf-8")

    request = urllib.request.Request(
        f"{API}/{method}",
        data=encoded,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=40
    ) as response:

        raw = response.read().decode("utf-8")

        return json.loads(raw)


# ==========================================
# XABAR YUBORISH
# ==========================================

def send_message(chat_id, text):

    try:

        result = telegram(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text
            }
        )

        if result.get("ok"):
            print("Xabar yuborildi.")
        else:
            print("sendMessage xatosi:", result)

    except Exception as e:

        print("Xabar yuborishda xato:", e)


# ==========================================
# TELEGRAM BOT
# ==========================================

def bot_loop():

    offset = 0

    print("Telegram bot ishga tushmoqda...")

    # Eski webhookni o'chirish
    try:

        result = telegram(
            "deleteWebhook",
            {
                "drop_pending_updates": False
            }
        )

        print("Webhook natijasi:", result)

    except Exception as e:

        print("Webhook o'chirishda xato:", e)


    # Bot haqida tekshiruv
    try:

        me = telegram("getMe")

        if me.get("ok"):

            bot_name = me["result"].get("first_name", "")
            bot_username = me["result"].get("username", "")

            print(
                f"Bot topildi: {bot_name} @{bot_username}"
            )

        else:

            print("BOT TOKEN ishlamadi:", me)
            return

    except Exception as e:

        print("getMe xatosi:", e)
        return


    print("Telegram polling boshlandi.")


    # ======================================
    # ASOSIY POLLING
    # ======================================

    while True:

        try:

            result = telegram(
                "getUpdates",
                {
                    "offset": offset,
                    "timeout": 25,
                    "allowed_updates": json.dumps(
                        ["message"]
                    )
                }
            )


            if not result.get("ok"):

                print(
                    "getUpdates xatosi:",
                    result
                )

                time.sleep(5)
                continue


            updates = result.get(
                "result",
                []
            )


            for update in updates:

                # Keyingi update
                offset = update["update_id"] + 1


                message = update.get(
                    "message"
                )

                if not message:
                    continue


                chat = message.get(
                    "chat"
                )

                if not chat:
                    continue


                chat_id = chat.get(
                    "id"
                )

                text = message.get(
                    "text",
                    ""
                ).strip()


                print(
                    f"Xabar keldi: {text}"
                )


                # ==================================
                # /start
                # ==================================

                if text == "/start":

                    send_message(
                        chat_id,
                        "Salom! 👋\n\n"
                        "RS online bot ishga tushdi! ✅\n\n"
                        "Bot sizning xabarlaringizni qabul qiladi."
                    )


                # ==================================
                # /help
                # ==================================

                elif text == "/help":

                    send_message(
                        chat_id,
                        "RS online bot yordam bo‘limi 🤖\n\n"
                        "/start — botni ishga tushirish\n"
                        "/help — yordam"
                    )


                # ==================================
                # /status
                # ==================================

                elif text == "/status":

                    send_message(
                        chat_id,
                        "Bot holati: ONLINE ✅"
                    )


                # ==================================
                # BOSHQA XABAR
                # ==================================

                else:

                    send_message(
                        chat_id,
                        "Xabaringiz qabul qilindi ✅\n\n"
                        f"Siz yozdingiz:\n{text}"
                    )


        except Exception as e:

            print(
                "Polling xatosi:",
                repr(e)
            )

            time.sleep(5)


# ==========================================
# RENDER HEALTH SERVER
# ==========================================

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


    def do_HEAD(self):

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain"
        )

        self.end_headers()


    def log_message(
        self,
        format,
        *args
    ):

        return


# ==========================================
# RENDER SERVER
# ==========================================

def start_server():

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )


    server = HTTPServer(
        (
            "0.0.0.0",
            port
        ),
        Handler
    )


    print(
        f"Render server ishga tushdi: {port}"
    )


    server.serve_forever()


# ==========================================
# MAIN
# ==========================================

def main():

    print("==============================")
    print("RS ONLINE BOT")
    print("==============================")


    # Render serverini alohida threadda
    server_thread = threading.Thread(
        target=start_server,
        daemon=True
    )

    server_thread.start()


    # Telegram botni ASOSIY jarayonda
    # ishga tushiramiz
    bot_loop()


# ==========================================
# START
# ==========================================

if __name__ == "__main__":

    main()