from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error  # <-- Добавили для перехвата точных HTTP-ошибок
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
            self.wfile.write(json.dumps(err).encode('utf-8'))
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
                
        except urllib.error.HTTPError as e:
            # Сюда мы падаем, если Groq отвечает 403, 400 и т.д.
            self.send_response(200)  # Отдаем боту 200, чтобы он не сломался, а прочитал текст ошибки
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                # Пытаемся прочитать точный ответ (JSON) от серверов Groq
                error_body = e.read().decode('utf-8')
                error_text = f"❌ Точная ошибка Groq (HTTP {e.code}):\n{error_body}"
            except Exception as read_e:
                error_text = f"❌ Ошибка Groq (HTTP {e.code}), не удалось прочитать тело ответа: {str(read_e)}"
                
            error_msg = {"choices": [{"message": {"content": error_text}}]}
            self.wfile.write(json.dumps(error_msg).encode('utf-8'))
            
        except Exception as e:
            # Это на случай других ошибок (например, таймаут сети)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_text = f"❌ Системная ошибка прокси: {str(e)}"
            error_msg = {"choices": [{"message": {"content": error_text}}]}
            self.wfile.write(json.dumps(error_msg).encode('utf-8'))
