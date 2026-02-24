from http.server import BaseHTTPRequestHandler
import sys
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        
        output = [
            "Python runtime works!",
            f"PYTHONPATH: {sys.path}",
            f"CWD: {os.getcwd()}"
        ]
        
        try:
            import tonesoul
            output.append(f"tonesoul module found at: {tonesoul.__file__}")
        except ImportError as e:
            output.append(f"ImportError: {e}")
            
        self.wfile.write('\n'.join(output).encode('utf-8'))
