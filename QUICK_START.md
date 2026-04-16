# 🎵 SWAM MIDI Player v2 - Quick Start Guide

## What Changed?

**Problem:** The old HTML player lost CC events because `midi-player-js` library failed to parse them.

**Solution:** Hybrid Python + Browser approach:
- ✅ Python (`mido`) parses MIDI perfectly → 45/45 CC events
- ✅ WebSocket streams events to browser
- ✅ Browser sends to SWAM via Web MIDI API
- ✅ **No C++ compiler needed!**

## How to Use

### 1. Start the Server

**Option A - One-Click Launcher (Windows):**
```powershell
.\start_player.bat
```

**Option B - Python Launcher (Any OS):**
```powershell
python start_player.py
```

**Option C - Manual:**
```powershell
# Terminal 1 - Python Server
python scripts\midi_websocket_server.py

# Terminal 2 - Open Browser
start swam_violin_player_v2.html
```

### 2. Set Up MIDI Routing

**Windows:**
1. Install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Create a virtual port (e.g., "loopMIDI Port")
3. In SWAM Violin → Preferences → MIDI, select that port

**macOS:**
1. Open Audio MIDI Setup → MIDI Studio
2. Double-click "IAC Driver"  
3. Check "Device is online"
4. In SWAM Violin → Preferences → MIDI, select "IAC Bus 1"

### 3. Use the Player

1. Browser will show: "Connected → [Your MIDI Port]"
2. Select a MIDI file from the dropdown
3. You'll see: **"CC Events: 45"** (not 0!)
4. Click **Play**
5. SWAM plays with perfect CC delivery

## What You Should See

**Python Terminal:**
```
✅ MIDI Parser initialized
▶️  Server running on ws://localhost:8765

🔌 Browser connected from ('127.0.0.1', xxxxx)

📁 Loaded: pala1_violin_swam.mid
   CC events: 45
   CC numbers: [1, 2, 11, 17, 20, 21, 64, 74]

▶️  Playing MIDI file...
   Total events to send: 66
   ✅ Playback complete (66 events sent)
```

**Browser Console (F12):**
```
✅ Connected to Python MIDI server
✅ MIDI Output: loopMIDI Port
📁 File loaded: pala1_violin_swam.mid
   CC Events: 45 ✅
   CC Numbers: 1, 2, 11, 17, 20, 21, 64, 74
```

## Troubleshooting

### Browser Shows "Server Not Running"
- Make sure Python server is running (see Terminal 1)
- Check the server shows: `▶️  Server running on ws://localhost:8765`

### "No MIDI Output Found"
- Install loopMIDI (Windows) or enable IAC Driver (macOS)
- Reload the browser page after setting up MIDI
- Check browser console for MIDI access errors

### No Sound from SWAM
- Verify SWAM is running
- Check SWAM's MIDI input matches your virtual port
- Verify SWAM's audio output is working (test with built-in sounds)

### Server Won't Start - Missing Dependencies
```powershell
pip install websockets
```

Note: `mido` should already be installed from `requirements.txt`

## Testing the Setup

1. Run Python diagnostic:
```powershell
python scripts\analyze_midi_cc.py midi_output\pala1_violin_swam.mid
```

Should show:
```
✅ This file SHOULD show CC events in the HTML player.
   Total CC messages: 45
```

2. Start the server and player
3. Load `pala1_violin_swam.mid`
4. Verify in browser: **"CC Events: 45"**

If you see "CC Events: 0" - something is wrong!

## Architecture

```
┌─────────────────────────────────────────────────┐
│  swam_violin_player_v2.html (Browser)          │
│  • Beautiful UI                                  │
│  • Web MIDI API output                          │
│  • Visualizations                               │
└───────────▲──────────────┬──────────────────────┘
            │              │
        WebSocket     MIDI Messages
        Connection    via Web MIDI API
            │              │
            │              ▼
┌───────────┴──────────────────────────────────────┐
│  midi_websocket_server.py                        │
│  • Parses MIDI with mido (100% accurate)        │
│  • Streams events with timing                    │
│  • No MIDI hardware access needed                │
└───────────────────────────┬──────────────────────┘
                            │
                        Reads from
                            │
                            ▼
                    ┌──────────────┐
                    │  MIDI Files  │
                    │  (45 CC msgs)│
                    └──────────────┘
```

## Next Steps

Once working, you can:
- Add CC curve visualization to browser
- Implement A/B file comparison
- Add real-time CC editing
- Create preset management system

Questions? Check browser console (F12) and Python terminal for detailed logging!
