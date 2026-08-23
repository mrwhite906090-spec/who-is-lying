from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        response_data = {"status": "ok", "message": "Детективный департамент 'Кто лжёт?' работает!"}
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Сервер запущен на порту {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
