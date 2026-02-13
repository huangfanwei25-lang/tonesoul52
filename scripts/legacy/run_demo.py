"""
ToneSoul Demo Launcher
Starts the API server and opens the browser.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def main():
    root = Path(__file__).parent
    api_path = root / "apps" / "api" / "server.py"

    print("=" * 50)
    print("  ToneSoul Demo")
    print("=" * 50)

    # Check dependencies
    try:
        import flask
        import flask_cors

        print("✓ Flask dependencies found")
    except ImportError:
        print("Installing Flask dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors", "-q"])
        print("✓ Dependencies installed")

    # Start API server
    print("Starting API server...")
    print(f"  Server file: {api_path}")

    server = subprocess.Popen([sys.executable, str(api_path)], cwd=str(root))

    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)

    # Open browser
    url = "http://localhost:5000"
    print(f"Opening browser: {url}")
    webbrowser.open(url)

    print()
    print("=" * 50)
    print("  Demo is running!")
    print("  Press Ctrl+C to stop")
    print("=" * 50)

    try:
        server.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.terminate()
        server.wait()
        print("Done.")


if __name__ == "__main__":
    main()
