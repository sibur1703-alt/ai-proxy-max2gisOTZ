from http.server import BaseHTTPRequestHandler
import urllib.request
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Проверяем наличие ключа
        api_key = os.environ.get("GROQ_API_KEY")
        
        if not api_key:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            err = {"choices": [{"message": {"content": "❌ Ошибка: GROQ_API_KEY не найден в настройках Vercel!"}}]}
            self.wfile.write(json.dumps(err).encode())
            return

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            req = urllib.request.Request(url, data=post_data, headers=headers, method='POST')
            with urllib.request.urlopen(req) as response:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Выводим саму ошибку от Groq, чтобы понять причину (например, неверный ключ)
            error_text = f"❌ Ошибка Groq API: {str(e)}"
            error_msg = {"choices": [{"message": {"content": error_text}}]}
            self.wfile.write(json.dumps(error_msg).encode())
