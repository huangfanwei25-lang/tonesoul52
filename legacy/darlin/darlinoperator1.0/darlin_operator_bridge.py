"""
Darlin Operator Bridge - Ollama Integration
============================================
This server emulates the DarlinOperator API and forwards LLM requests to Ollama.

Based on reverse engineering of Darlin game logs.
"""

import json
import http.server
import socketserver
import urllib.request
import urllib.error
import threading
import os
from datetime import datetime

# Configuration
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma3:4b"

# Service status codes (from service_name_to_code_config.json)
SERVICE_CODES = {
    "DarlinListening": "W001",
    "DarlinTTS": "W002", 
    "DarlinSong": "W003",
    "DarlinAI": "W004",
    "DarlinEmpathy": "W005",
    "DarlinTranslate": "W006",
    "DarlinKnowledge": "W007",
    "DarlinMemory": "W008",
    "DarlinLogic": "W009",
    "postgresql-x64-17": "W010"
}


def log(message: str):
    """Log with timestamp to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)
    try:
        with open("bridge_debug.log", "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except:
        pass


def call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call Ollama API and return response"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "")
    except Exception as e:
        log(f"Ollama error: {e}")
        return f"Error: {e}"


def get_ollama_embedding(text: str) -> list:
    """Get embedding from Ollama"""
    try:
        payload = {"model": "nomic-embed-text", "prompt": text}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/embeddings",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("embedding", [])
    except Exception as e:
        log(f"Embedding error: {e}")
        return []


class DarlinOperatorHandler(http.server.BaseHTTPRequestHandler):
    """Handler for Darlin Operator API requests"""
    
    def log_message(self, format, *args):
        """Override to use our logging"""
        log(f"[HTTP] {args[0]}")
    
    def send_json(self, data: dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        log(f"GET {self.path}")
        
        # Health check / status endpoints
        if self.path == "/" or self.path == "/status":
            self.send_json({
                "status": "ok",
                "version": "2025-08-15-dynamic-gpu",
                "bridge": "ollama",
                "services": {name: "running" for name in SERVICE_CODES.keys()}
            })
        
        # Service status check
        elif self.path.startswith("/service/"):
            service_name = self.path.split("/service/")[1]
            self.send_json({
                "service": service_name,
                "status": "running",
                "code": SERVICE_CODES.get(service_name, "W000")
            })
        
        # Camera permission check (mock)
        elif "camera" in self.path.lower() or "permission" in self.path.lower():
            self.send_json({"granted": True})
        
        else:
            self.send_json({"error": "Unknown endpoint", "path": self.path}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""
        
        log(f"POST {self.path}")
        if body:
            try:
                data = json.loads(body)
                log(f"  Body: {json.dumps(data, ensure_ascii=False)[:200]}...")
            except:
                log(f"  Body (raw): {body[:200]}...")
                data = {}
        else:
            data = {}
        
        # AI/Chat endpoint
        if "ai" in self.path.lower() or "chat" in self.path.lower() or "generate" in self.path.lower():
            prompt = data.get("prompt", data.get("message", data.get("text", "")))
            if prompt:
                response = call_ollama(prompt)
                self.send_json({"response": response, "status": "ok"})
            else:
                self.send_json({"error": "No prompt provided"}, 400)
        
        # Embedding endpoint
        elif "embed" in self.path.lower() or "translate" in self.path.lower():
            text = data.get("text", data.get("input", ""))
            if text:
                embedding = get_ollama_embedding(text)
                self.send_json({"embedding": embedding, "status": "ok"})
            else:
                self.send_json({"error": "No text provided"}, 400)
        
        # Service control (start/stop)
        elif "service" in self.path.lower():
            self.send_json({"status": "ok", "message": "Service operation mocked"})
        
        # Generic success for unknown endpoints (permissive mode)
        else:
            log(f"  Unknown endpoint, returning mock success")
            self.send_json({"status": "ok", "message": "Mocked response"})


def run_server_on_port(port):
    """Start server on a specific port"""
    try:
        # Allow reusing address to avoid "Address already in use" errors
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer(("", port), DarlinOperatorHandler)
        log(f"Listening on port {port}")
        server.serve_forever()
    except OSError as e:
        log(f"Port {port} failed: {e}")

def run_server():
    """Start the operator bridge server on multiple ports"""
    ports = [8080, 9000, 5000, 3000, 13579, 8000, 80]
    log(f"=" * 50)
    log(f"Darlin Operator Bridge Started (Multi-Port)")
    log(f"Ollama backend: {OLLAMA_URL}")
    log(f"Default model: {DEFAULT_MODEL}")
    log(f"=" * 50)
    
    threads = []
    for port in ports:
        t = threading.Thread(target=run_server_on_port, args=(port,))
        t.daemon = True
        t.start()
        threads.append(t)
        
    log("Waiting for Darlin game connections on any active port...")
    
    # Keep main thread alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_server()
