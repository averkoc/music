#!/usr/bin/env python3
"""
WebSocket MIDI Server for HTML Player
Parses MIDI files with mido and streams events to browser via WebSocket
Also serves HTML/static files to avoid file:// protocol issues

Usage:
    pip install websockets
    python midi_websocket_server.py
    Then open http://localhost:8000 in browser
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from http.server import SimpleHTTPRequestHandler
import socketserver
import threading

import mido
from mido import MidiFile

try:
    import websockets.server
    import websockets
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install websockets")
    print("\nNote: mido should already be installed (check requirements.txt)")
    exit(1)


class MidiPlayer:
    """Server-side MIDI parser - Browser handles MIDI output via Web MIDI API"""
    
    def __init__(self):
        self.current_file: Optional[MidiFile] = None
        self.is_playing = False
        self.play_task: Optional[asyncio.Task] = None
        self.tempo_scale = 1.0
        self.current_tick = 0
        self.total_ticks = 0
        
        print("\n✅ MIDI Parser initialized")
        print("   Browser will handle MIDI output via Web MIDI API")
    
    def load_file(self, filepath: str) -> Dict:
        """Load MIDI file and analyze it"""
        try:
            path = Path(filepath)
            self.current_file = MidiFile(path)
            
            # Analyze file
            messages = []
            for track in self.current_file.tracks:
                messages.extend(track)
            
            # Count events
            cc_msgs = [m for m in messages if m.type == 'control_change']
            note_msgs = [m for m in messages if m.type in ('note_on', 'note_off')]
            bend_msgs = [m for m in messages if m.type == 'pitchwheel']
            
            # Get CC breakdown
            cc_by_number = {}
            for msg in cc_msgs:
                cc_num = msg.control
                cc_by_number[cc_num] = cc_by_number.get(cc_num, 0) + 1
            
            # Calculate total ticks
            self.total_ticks = 0
            for track in self.current_file.tracks:
                track_ticks = sum(msg.time for msg in track)
                self.total_ticks = max(self.total_ticks, track_ticks)
            
            print(f"\n📁 Loaded: {path.name}")
            print(f"   CC events: {len(cc_msgs)}")
            print(f"   CC numbers: {sorted(cc_by_number.keys())}")
            
            return {
                'success': True,
                'filename': path.name,
                'size': path.stat().st_size,
                'format': self.current_file.type,
                'ticks_per_beat': self.current_file.ticks_per_beat,
                'tracks': len(self.current_file.tracks),
                'events': {
                    'notes': len(note_msgs),
                    'cc': len(cc_msgs),
                    'pitch_bend': len(bend_msgs),
                },
                'cc_numbers': sorted(cc_by_number.keys()),
                'cc_counts': cc_by_number,
                'total_ticks': self.total_ticks,
            }
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def play(self, websocket):
        """Stream MIDI events to browser with timing - browser sends to SWAM"""
        if not self.current_file:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'No file loaded'
            }))
            return
        
        self.is_playing = True
        self.current_tick = 0
        
        print(f"\n▶️  Playing MIDI file...")
        
        # Build tempo map for handling tempo changes throughout the song
        tempo_map = []  # List of (tick, tempo_microseconds)
        default_tempo = 500000  # 120 BPM
        
        for track in self.current_file.tracks:
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                if msg.type == 'set_tempo':
                    tempo_map.append((abs_time, msg.tempo))
        
        # Sort tempo map by tick
        tempo_map.sort(key=lambda x: x[0])
        
        # If no tempo events, use default
        if not tempo_map:
            tempo_map.append((0, default_tempo))
        
        # Display initial tempo
        initial_bpm = mido.tempo2bpm(tempo_map[0][1])
        print(f"   🎵 Initial tempo: {initial_bpm:.0f} BPM")
        if len(tempo_map) > 1:
            print(f"   🎵 Tempo changes detected: {len(tempo_map)} tempo events")
        
        # Merge all tracks into single timeline with absolute timing
        events = []
        for track in self.current_file.tracks:
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                if not msg.is_meta:
                    events.append({
                        'time': abs_time,
                        'msg': msg
                    })
        
        # Sort by time
        events.sort(key=lambda x: x['time'])
        
        print(f"   Total events to send: {len(events)}")
        
        # Stream events with precise timing
        playback_start = time.time()
        events_sent = 0
        completed = False
        
        # Pre-calculate absolute time for each event (in seconds)
        # This accounts for tempo changes and is more efficient
        event_times = []
        current_time_seconds = 0.0
        last_tick = 0
        tempo_index = 0
        current_tempo = tempo_map[0][1]
        
        for event in events:
            tick = event['time']
            
            # Process any tempo changes that occurred before this event
            while tempo_index < len(tempo_map) - 1 and tempo_map[tempo_index + 1][0] <= tick:
                # Calculate time up to the tempo change
                tempo_change_tick = tempo_map[tempo_index + 1][0]
                if tempo_change_tick > last_tick:
                    delta = tempo_change_tick - last_tick
                    current_time_seconds += mido.tick2second(
                        delta,
                        self.current_file.ticks_per_beat,
                        current_tempo
                    )
                    last_tick = tempo_change_tick
                
                # Update to new tempo
                tempo_index += 1
                current_tempo = tempo_map[tempo_index][1]
            
            # Calculate time from last processed tick to this event
            if tick > last_tick:
                delta = tick - last_tick
                current_time_seconds += mido.tick2second(
                    delta,
                    self.current_file.ticks_per_beat,
                    current_tempo
                )
                last_tick = tick
            
            event_times.append(current_time_seconds / self.tempo_scale)
        
        print(f"   📊 Total duration: {event_times[-1] if event_times else 0:.1f}s (at {int(self.tempo_scale * 100)}% speed)")
        
        # Now stream events with precise timing
        for i, event in enumerate(events):
            if not self.is_playing:
                print("   ⏹️  Playback stopped by user")
                break
            
            msg = event['msg']
            expected_time = event_times[i]
            
            # Calculate how long to wait (with drift compensation)
            elapsed = time.time() - playback_start
            wait_time = expected_time - elapsed
            
            if wait_time > 0:
                # Chunked sleep for responsiveness
                sleep_chunks = max(1, int(wait_time / 0.05))  # 50ms chunks
                chunk_time = wait_time / sleep_chunks
                for _ in range(sleep_chunks):
                    if not self.is_playing:
                        break
                    await asyncio.sleep(chunk_time)
            
            # Check again after sleep - if stopped during sleep, exit immediately
            if not self.is_playing:
                print("   ⏹️  Playback stopped by user")
                break
            
            # Send MIDI event to browser
            try:
                event_data = {
                    'type': 'midi_event',
                    'event': {
                        'name': msg.type,
                        'bytes': list(msg.bytes()) if hasattr(msg, 'bytes') else None,
                        'channel': getattr(msg, 'channel', None),
                        'note': getattr(msg, 'note', None),
                        'velocity': getattr(msg, 'velocity', None),
                        'control': getattr(msg, 'control', None),
                        'value': getattr(msg, 'value', None),
                        'pitch': getattr(msg, 'pitch', None),
                    }
                }
                await websocket.send(json.dumps(event_data))
                events_sent += 1
                
            except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedError):
                # Connection closed during playback - stop silently
                self.is_playing = False
                print("   🔌 Connection lost during playback")
                break
            except Exception as e:
                print(f"   ❌ Error sending event: {e}")
                self.is_playing = False
                break
            
            # Update progress (based on time instead of ticks for accuracy)
            if event_times:
                progress = (expected_time / event_times[-1] * 100)
            else:
                progress = 0
            
            # Send progress update periodically
            if events_sent % 20 == 0:  # Every 20 events
                await websocket.send(json.dumps({
                    'type': 'progress',
                    'percent': progress,
                    'elapsed': time.time() - playback_start,
                    'total_duration': event_times[-1] if event_times else 0
                }))
        
        # Mark as completed if we finished all events
        if events_sent == len(events):
            completed = True
        
        # Playback complete or stopped
        self.is_playing = False
        
        try:
            if completed:
                actual_duration = time.time() - playback_start
                expected_duration = event_times[-1] if event_times else 0
                timing_error = abs(actual_duration - expected_duration)
                
                print(f"   ✅ Playback complete ({events_sent} events sent)")
                print(f"   ⏱️  Timing: {actual_duration:.2f}s actual vs {expected_duration:.2f}s expected (error: {timing_error:.3f}s)")
                
                await websocket.send(json.dumps({
                    'type': 'playback_complete'
                }))
            else:
                await websocket.send(json.dumps({
                    'type': 'stopped'
                }))
        except:
            pass  # Connection may be closed
    
    def stop(self):
        """Stop playback - browser will handle all notes off"""
        if self.is_playing:
            self.is_playing = False
            if self.play_task and not self.play_task.done():
                self.play_task.cancel()
            print("   ⏹️  Stop requested")
    
    def set_tempo(self, scale: float):
        """Set tempo scaling (1.0 = normal, 0.5 = half speed, 2.0 = double)"""
        self.tempo_scale = max(0.25, min(4.0, scale))
        print(f"   🎵 Tempo set to {int(scale * 100)}%")


# Global player instance
player = MidiPlayer()

# Track connected clients for auto-shutdown
connected_clients = set()
shutdown_task = None
server_stop_event = None


async def handle_client(websocket, path):
    """Handle WebSocket messages from browser"""
    global shutdown_task
    
    print(f"\n🔌 Browser connected from {websocket.remote_address}")
    connected_clients.add(websocket)
    
    # Cancel any pending shutdown since we have a client
    if shutdown_task and not shutdown_task.done():
        shutdown_task.cancel()
        print("   ⏸️  Auto-shutdown cancelled (client connected)")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'list_files':
                # Scan midi_output directory for MIDI files
                midi_files = []
                midi_output_dir = Path('midi_output')
                
                if midi_output_dir.exists():
                    for file_path in midi_output_dir.glob('*.mid'):
                        midi_files.append({
                            'path': str(file_path.as_posix()),
                            'name': file_path.name
                        })
                    # Also check for .midi extension
                    for file_path in midi_output_dir.glob('*.midi'):
                        midi_files.append({
                            'path': str(file_path.as_posix()),
                            'name': file_path.name
                        })
                
                # Sort by name
                midi_files.sort(key=lambda x: x['name'].lower())
                
                await websocket.send(json.dumps({
                    'type': 'file_list',
                    'files': midi_files
                }))
            
            elif command == 'load_file':
                filepath = data.get('filepath')
                result = player.load_file(filepath)
                await websocket.send(json.dumps({
                    'type': 'file_loaded',
                    **result
                }))
            
            elif command == 'load_file_data':
                # Load MIDI file from binary data sent by browser
                filename = data.get('filename', 'uploaded.mid')
                file_data = data.get('data', [])
                
                try:
                    # Convert to bytes and save to temp location
                    import tempfile
                    bytes_data = bytes(file_data)
                    
                    # Create temp file
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as temp_file:
                        temp_file.write(bytes_data)
                        temp_path = temp_file.name
                    
                    # Load the file
                    result = player.load_file(temp_path)
                    
                    # Update filename in result to show original name
                    if result.get('success'):
                        result['filename'] = filename
                    
                    await websocket.send(json.dumps({
                        'type': 'file_loaded',
                        **result
                    }))
                    
                    print(f"✅ Loaded uploaded file: {filename}")
                    
                except Exception as e:
                    print(f"❌ Error loading uploaded file: {e}")
                    await websocket.send(json.dumps({
                        'type': 'file_loaded',
                        'success': False,
                        'error': str(e)
                    }))
            
            elif command == 'play':
                # Cancel any existing playback task first
                if player.play_task and not player.play_task.done():
                    player.play_task.cancel()
                    try:
                        await player.play_task
                    except asyncio.CancelledError:
                        pass
                
                # Start new playback task
                player.play_task = asyncio.create_task(player.play(websocket))
            
            elif command == 'stop':
                player.stop()
                await websocket.send(json.dumps({
                    'type': 'stopped'
                }))
            
            elif command == 'set_tempo':
                tempo_scale = data.get('scale', 1.0)
                player.set_tempo(tempo_scale)
                await websocket.send(json.dumps({
                    'type': 'tempo_changed',
                    'scale': player.tempo_scale
                }))
    
    except websockets.exceptions.ConnectionClosed:
        print("🔌 Browser disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
        except:
            pass
    finally:
        # Remove client from tracking
        connected_clients.discard(websocket)
        
        # If no clients left, schedule shutdown
        if len(connected_clients) == 0:
            print("\n⏳ No clients connected. Server will shut down in 3 seconds...")
            print("   (Reconnect within 3 seconds to cancel)")
            shutdown_task = asyncio.create_task(schedule_shutdown())


async def schedule_shutdown():
    """Wait a few seconds then trigger server shutdown"""
    try:
        await asyncio.sleep(3)
        print("\n👋 Shutting down server (no clients connected)")
        if server_stop_event:
            server_stop_event.set()
    except asyncio.CancelledError:
        # Shutdown was cancelled because a client reconnected
        pass


async def main():
    """Start WebSocket server and HTTP server"""
    global server_stop_event
    
    print("\n" + "="*60)
    print("🎵 MIDI WebSocket Server (Hybrid Mode)")
    print("="*60)
    print("\n📌 Architecture:")
    print("   Python (mido) → Parse MIDI perfectly → WebSocket")
    print("   Browser → Receive events → Web MIDI API → SWAM")
    print("\n✅ No C++ compilation needed!")
    print("✅ Auto-shutdown when browser closes")
    
    # Start HTTP server in background for serving HTML
    def start_http_server():
        # Change to project root directory
        import os
        os.chdir(Path(__file__).parent.parent)
        
        # Use ThreadingTCPServer to handle concurrent requests
        class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
            """Custom handler that doesn't log connection errors"""
            def log_message(self, format, *args):
                # Only log successful requests
                if args[1][0] == '2':  # 2xx status codes
                    super().log_message(format, *args)
        
        httpd = socketserver.ThreadingTCPServer(("", 8000), QuietHTTPRequestHandler)
        httpd.allow_reuse_address = True
        print(f"▶️  HTTP Server running on http://localhost:8000")
        httpd.serve_forever()
    
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Create stop event
    server_stop_event = asyncio.Event()
    
    # Start WebSocket server
    async with websockets.server.serve(handle_client, "localhost", 8765):
        print(f"▶️  WebSocket Server running on ws://localhost:8765")
        print(f"\n🌐 Open in browser: http://localhost:8000/swam_violin_player_v2.html")
        print(f"\n   Server will auto-shutdown when browser closes")
        print(f"   Press Ctrl+C to stop manually\n")
        await server_stop_event.wait()  # Wait until shutdown is triggered


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
