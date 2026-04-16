#!/usr/bin/env python3
"""
SWAM MIDI Player Launcher
Starts the WebSocket server and opens the HTML player in your browser
Works on Windows, macOS, and Linux
"""

import subprocess
import webbrowser
import time
import sys
import signal
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import websockets
        import mido
        return True
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e.name}")
        print("\nInstall with:")
        print("  pip install websockets")
        print("\nNote: mido should already be installed from requirements.txt")
        return False

def main():
    print("\n" + "="*50)
    print("  🎵 SWAM MIDI Player Launcher")
    print("="*50 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Get paths
    script_dir = Path(__file__).parent
    server_script = script_dir / "scripts" / "midi_websocket_server.py"
    html_file = script_dir / "swam_violin_player_v2.html"
    
    if not server_script.exists():
        print(f"❌ Server script not found: {server_script}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    if not html_file.exists():
        print(f"⚠️  HTML file not found: {html_file}")
        print("   Will create it when server starts...")
    
    # Start server
    print("▶️  Starting MIDI WebSocket server...")
    server_process = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait for server to initialize
    time.sleep(2)
    
    # Check if server started successfully
    if server_process.poll() is not None:
        print("❌ Server failed to start!")
        print("\nServer output:")
        print(server_process.stdout.read())
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("✅ Server running on ws://localhost:8765")
    
    # Open HTML in browser
    if html_file.exists():
        print(f"🌐 Opening player in browser...")
        webbrowser.open(html_file.as_uri())
    else:
        print(f"\n⚠️  Please open this URL in your browser:")
        print(f"   file:///{html_file.absolute()}")
    
    print("\n" + "="*50)
    print("  Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    # Keep running and handle Ctrl+C
    def signal_handler(sig, frame):
        print("\n\n👋 Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("✅ Server stopped. Goodbye!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Stream server output
    try:
        for line in server_process.stdout:
            print(line, end='')
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()
