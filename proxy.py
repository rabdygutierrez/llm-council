# proxy.py — usa Ollama local, sin API key ni saldo
# 1. Instala Ollama: https://ollama.com
# 2. Corre: ollama pull llama3.2
# 3. Corre: python proxy.py
# 4. Abre: http://localhost:8080

import http.server
import json
import urllib.request

PORT = 8080
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"  {format % args}")

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html", "/generador_casos_prueba.html"):
            try:
                with open("generador_casos_prueba.html", "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Pon generador_casos_prueba.html en la misma carpeta")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/v1/messages":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            messages = body.get("messages", [])

            ollama_body = json.dumps({
                "model": MODEL,
                "messages": messages,
                "stream": False
            }).encode()

            try:
                req = urllib.request.Request(
                    OLLAMA_URL,
                    data=ollama_body,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req) as r:
                    result = json.loads(r.read())

                text = result.get("message", {}).get("content", "Sin respuesta")
                payload = json.dumps({
                    "content": [{"type": "text", "text": text}]
                }).encode()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(payload)

            except Exception as e:
                error = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(error)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"✅  Servidor en http://localhost:{PORT}")
    print(f"    Usando Ollama con modelo: {MODEL}")
    print(f"    Asegúrate de que Ollama esté corriendo (ollama serve)")
    with http.server.HTTPServer(("", PORT), Handler) as server:
        server.serve_forever()
