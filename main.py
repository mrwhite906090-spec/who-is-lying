import os
import json
import urllib.request
import urllib.parse
import time

TOKEN = os.environ.get("TELEGRAM_TOKEN", "8342175799:AAEVDjSw0jvYcsUxUjfx9DUKTI75iW9FVK4")
PORT = int(os.environ.get("PORT", 10000))

# Простейший веб-сервер для Render, чтобы он не выключал приложение
import http.server
import socketserver

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telegram bot is running!")

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    import threading
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("Bot started, waiting for token...")
    # Здесь позже добавим логику бота, когда ты укажешь токен
    while True:
        time.sleep(10)
