from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Берем ключ Cerebras из Vercel
        api_key = os.environ.get("CEREBRAS_API_KEY")
        
        if not api_key:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            err = {"choices": [{"message": {"content": "❌ Ошибка: CEREBRAS_API_KEY не найден в Vercel!"}}]}
            self.wfile.write(json.dumps(err).encode('utf-8'))
            return

        url = "https://api.cerebras.ai/v1/chat/completions"
        
        # 💥 МАГИЯ ЗДЕСЬ: Прикидываемся настоящим браузером Chrome, чтобы обойти ошибку 1010
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
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
                error_text = f"❌ Ошибка Cerebras (HTTP {e.code}):\n{error_body}"
            except:
                error_text = f"❌ Ошибка Cerebras (HTTP {e.code})"
            self.wfile.write(json.dumps({"choices": [{"message": {"content": error_text}}]}).encode('utf-8'))
