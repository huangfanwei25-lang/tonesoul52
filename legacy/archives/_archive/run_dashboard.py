
import subprocess
import sys
import os

if __name__ == "__main__":
    # Get the absolute path to the streamlit app
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "body", "dashboard", "app.py")
    
    print(f"🚀 Launching ToneSoul Dashboard...")
    print(f"📄 App Path: {app_path}")
    
    # Run streamlit as a subprocess
    # This is safer than importing stcli.main() recursively
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
