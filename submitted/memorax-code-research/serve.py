import http.server
import socketserver
import os
import json

socketserver.TCPServer.allow_reuse_address = True

stored_data = {}

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def guess_type(self, path):
        ctype = super().guess_type(path)
        if ctype.startswith('text/html') or path.endswith('.html'):
            return 'text/html; charset=utf-8'
        if ctype.startswith('text/plain') or path.endswith('.md'):
            return 'text/plain; charset=utf-8'
        if 'javascript' in ctype or path.endswith('.js'):
            return 'application/javascript; charset=utf-8'
        return ctype

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        stored_data['html'] = body.decode('utf-8')
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def do_GET(self):
        if self.path == '/styled-html':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'html': stored_data.get('html', '')}).encode('utf-8'))
        else:
            super().do_GET()

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with socketserver.TCPServer(("127.0.0.1", 9876), CORSHandler) as httpd:
    print("Serving on port 9876")
    httpd.serve_forever()
