import os
import json
import urllib.request
import urllib.parse
import time
import http.server
import socketserver
import threading

# Укажи свой токен прямо здесь или оставь переменной окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8342175799:AAEVDjSw0jvYcsUxUjfx9DUKTI75iW9FVK4")
PORT = int(os.environ.get("PORT", 10000))

# База загадок «Кто лжет?»
PUZZLES = [
    {
        "text": "🕵️‍♂️ **Дело о разбитой вазе**\n\nАлиса говорит: «Я читала книгу в спальне». \nБоб говорит: «Я мыл посуду на кухне». \nЧарли говорит: «В вазе стояли фальшивые цветы». \n\nКто-то из них врет. У кого алиби фальшивое?",
        "options": ["Алиса", "Боб", "Чарли"],
        "answer": "Боб" # (например)
    },
    {
        "text": "🕵️‍♂️ **Дело о ночном ограблении**\n\nСторож утверждает: «Я спал всю ночь и ничего не слышал». \nСобака не лаяла. \nСейф открыли родным ключом.\n\nКто врет?",
        "options": ["Сторож", "Собака", "Никто"],
        "answer": "Сторож"
    }
]

def send_telegram_request(method, data):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error sending request: {e}")
        return None

def send_message(chat_id, text):
    send_telegram_request("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

def handle_updates():
    offset = 0
    print("Бот запущен и слушает сообщения...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("ok"):
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        message = update.get("message")
                        if message and "text" in message:
                            chat_id = message["chat"]["id"]
                            text = message["text"].strip()
                            
                            if text == "/start":
                                send_message(chat_id, "Привет! Добро пожаловать в игру **«Кто лжет?»** 🕵️‍♂️\n\nНапиши /game, чтобы начать расследование!")
                            elif text == "/game" or text.lower() == "игра":
                                puzzle = PUZZLES[0]
                                send_message(chat_id, f"{puzzle['text']}\n\nНапиши свой вариант ответа (например: *Боб* или *Сторож*).")
                            else:
                                send_message(chat_id, f"Ты ответил: «{text}». Давай начнем заново, нажми /game")
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

# Веб-сервер для Render (чтобы хостинг не усыплял бота)
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Who is lying Telegram bot is running!")

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Web server running on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Запускаем обработчик Telegram
    handle_updates()
