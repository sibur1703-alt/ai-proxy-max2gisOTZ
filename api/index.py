from http.server import BaseHTTPRequestHandler
import urllib.request
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Ключ от нейросети берем из защищенных настроек Vercel
        api_key = os.environ.get("GROQ_API_KEY")
        
        # URL для Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        req = urllib.request.Request(
            url,
            data=post_data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(res_body)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
