import http.server
import socketserver
import json

PORT = int(os.environ.get("PORT", 10000)) if 'os' in globals() else 10000
import os

PORT = int(os.environ.get("PORT", 10000))

HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Кто лжет? - Игра</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; text-align: center; padding: 50px; }
        .card { background: #2a2a2a; padding: 20px; border-radius: 10px; display: inline-block; max-width: 400px; }
        button { background: #4CAF50; color: white; border: none; padding: 10px 20px; font-size: 16px; cursor: pointer; border-radius: 5px; margin-top: 15px; }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🕵️‍♂️ Кто лжет?</h1>
        <p id="statement">Загрузка загадки...</p>
        <button onclick="nextStmt()">Следующая</button>
    </div>
    <script>
        const statements = [
            { text: "Алиса говорит: 'Я никогда не была в Париже', но в ее кармане билет на самолет до Парижа.", lie: true },
            { text: "Борис утверждает, что умеет летать, спрыгнув со стула.", lie: true },
            { text: "Входная дверь была заперта изнутри, а ключи лежали на столе.", lie: false }
        ];
        let current = 0;
        function nextStmt() {
            current = (current + 1) % statements.length;
            document.getElementById('statement').innerText = statements[current].text;
        }
        document.getElementById('statement').innerText = statements[0].text;
    </script>
</body>
</html>
"""

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
