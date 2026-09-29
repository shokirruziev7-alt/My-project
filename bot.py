import os
import json
import urllib.request
import urllib.parse

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

API = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text):
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    }).encode()

    urllib.request.urlopen(
        urllib.request.Request(f"{API}/sendMessage", data=data)
    )


def get_updates(offset=None):
    url = f"{API}/getUpdates"
    if offset is not None:
        url += f"?offset={offset}"

    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def main():
    offset = None

    while True:
        updates = get_updates(offset)

        for update in updates.get("result", []):
            offset = update["update_id"] + 1

            message = update.get("message", {})
            chat = message.get("chat", {})
            text = message.get("text", "")

            if not chat:
                continue

            if text == "/start":
                send_message(
                    chat["id"],
                    "Salom! Bot ishlayapti. 🤖\n\n"
                    "Buyruqlar:\n"
                    "/start — boshlash\n"
                    "/help — yordam"
                )

            elif text == "/help":
                send_message(
                    chat["id"],
                    "Bu Telegram botning boshlang‘ich versiyasi."
                )

            else:
                send_message(
                    chat["id"],
                    f"Siz yozdingiz: {text}"
                )


if __name__ == "__main__":
    main()
