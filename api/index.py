from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Берем ключ OpenRouter (мы добавим его в Vercel на следующем шаге)
        api_key = os.environ.get("OPENROUTER_API_KEY")
        
        if not api_key:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            err = {"choices": [{"message": {"content": "❌ Ошибка: OPENROUTER_API_KEY не найден в Vercel!"}}]}
            self.wfile.write(json.dumps(err).encode('utf-8'))
            return

        # Перенаправляем запрос не в Groq, а в OpenRouter!
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://t.me/my_bot",
            "X-Title": "Max2GisBot",
            "Content-Type": "application/json"
        }
        
        try:
            req = urllib.request.Request(url, data=post_data, headers=headers, method='POST')
            with urllib.request.urlopen(req) as response:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                error_body = e.read().decode('utf-8')
                error_text = f"❌ Ошибка OpenRouter (HTTP {e.code}):\n{error_body}"
            except:
                error_text = f"❌ Ошибка OpenRouter (HTTP {e.code})"
            self.wfile.write(json.dumps({"choices": [{"message": {"content": error_text}}]}).encode('utf-8'))
