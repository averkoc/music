# MIDI Output Comparison Guide

This guide explains how to programmatically verify that the web player outputs identical MIDI to Ableton Live.

## Overview

The `record_midi_output.py` script records live MIDI output with microsecond-precision timestamps, then compares two recordings to detect timing differences.

## Requirements

```bash
pip install mido python-rtmidi
```

## Setup

### 1. Configure MIDI Routing

Both Ableton Live and the web player should send MIDI to the same virtual MIDI port that SWAM listens to (e.g., `loopMIDI Port`).

**Ableton Live:**
- Preferences → Link/Tempo/MIDI → MIDI Ports
- Enable "Track" output for loopMIDI Port

**Web Player:**
- Automatically detects and uses loopMIDI Port
- Check browser console to confirm: "✅ MIDI Output: loopMIDI Port"

### 2. Install MIDI Monitor (Optional Visual Verification)

Free tools to visualize MIDI messages:
- **Windows**: [MIDI-OX](http://www.midiox.com/)
- **Mac**: MIDI Monitor (from App Store)
- **Cross-platform**: [MIDIView](https://hautetechnique.com/midi/midiview/)

These let you see messages in real-time before doing programmatic comparison.

## Recording and Comparison Workflow

### Step 1: Record Ableton Live Output

1. Open Ableton Live
2. Load your processed MIDI file (e.g., `pala1_violin_swam.mid`)
3. Make sure SWAM is receiving and playing
4. Run the recorder:

```bash
python scripts/record_midi_output.py --record recordings/ableton_pala1.json --duration 60
```

5. Immediately press Play in Ableton Live
6. The script will record for 60 seconds (or until Ctrl+C)

### Step 2: Record Web Player Output

1. Open the web player: http://localhost:8000/swam_violin_player_v2.html
2. Select the same MIDI file (pala1_violin_swam.mid)
3. Run the recorder:

```bash
python scripts/record_midi_output.py --record recordings/webpage_pala1.json --duration 60
```

4. Immediately click Play in the web player
5. Let it record the full playback

### Step 3: Compare Recordings

```bash
python scripts/record_midi_output.py --compare recordings/ableton_pala1.json recordings/webpage_pala1.json
```

## Understanding the Comparison Report

### Note Timing Comparison

```
NOTE TIMING COMPARISON (First 20 notes)
==============================================================================
Note     Rec1 Time    Rec2 Time    Difference      Status
------------------------------------------------------------------------------
A3       0.500        0.502        +2.0 ms         ✓ PERFECT
B3       1.000        1.003        +3.0 ms         ✓ PERFECT
C4       1.500        1.548        +48.0 ms        ~OK (slight)
```

**Status meanings:**
- ✓ PERFECT: < 10ms difference (imperceptible)
- ~OK (slight): 10-50ms difference (measurable but acceptable)
- ⚠️ TIMING OFF: > 50ms difference (noticeable delay)
- ⚠️ WRONG NOTE: Different note at this position

### Timing Statistics

```
TIMING STATISTICS
==============================================================================

Average timing difference: +2.3 ms
Average absolute difference: 3.1 ms
Maximum timing error: 8.2 ms

✅ EXCELLENT: Timing accuracy within 10ms!
```

**Thresholds:**
- < 10ms: Excellent (human-imperceptible)
- < 50ms: Good (acceptable for musical performance)
- \> 50ms: Poor (needs investigation)

### CC Message Comparison

```
CC MESSAGE COMPARISON
==============================================================================

CC#   Name                 Rec1 Count   Rec2 Count   Difference
------------------------------------------------------------------------------
1     Modulation/Vibrato   45           45           +0
11    Expression           89           89           +0
64    Sustain             12           12           +0
74    Brightness          23           23           +0
```

**What to look for:**
- Identical counts = perfect match
- Small differences (±1-2) = rounding/timing variations (acceptable)
- Large differences = missing or extra CC messages (investigate)

### Overall Assessment

```
OVERALL ASSESSMENT
==============================================================================

✅ OUTPUTS ARE EQUIVALENT!
   Same message count, same CC distribution, excellent timing
```

## Troubleshooting

### "No MIDI input ports found"

**Problem:** Script can't find virtual MIDI ports

**Solutions:**
1. Make sure loopMIDI (Windows) or IAC Driver (Mac) is running
2. List available ports: `python scripts/record_midi_output.py --list-ports`
3. Specify port manually: `--port "loopMIDI Port"`

### Different Message Counts

**Possible causes:**
1. **Different file lengths**: Make sure both recordings captured full playback
2. **All-notes-off messages**: Web player sends CC120/123 when stopping (expected)
3. **Initialization**: Web player sends warmup CC messages (expected)

**What to do:**
- Focus on the note timing comparison (most important)
- Check if CC counts match (more important than total message count)

### Timing Drift

**Problem:** Early notes match perfectly, later notes drift apart

**Possible causes:**
1. Tempo not matching file tempo
2. Cumulative rounding errors
3. CPU load causing delays

**What to do:**
- Check server logs for "Timing: X.XXs actual vs X.XXs expected"
- Look for tempo change events in MIDI file
- Compare with different tempo slider settings

## Advanced Analysis

### Exporting to CSV for Spreadsheet Analysis

Modify the comparison script to output CSV:

```python
# In scripts/record_midi_output.py, add after comparison:
with open('comparison.csv', 'w') as f:
    f.write('Note,Rec1_Time,Rec2_Time,Difference_ms\n')
    for i, (data1, data2) in enumerate(zip(notes1, notes2)):
        time1, note1, _ = data1
        time2, note2, _ = data2
        diff_ms = (time2 - time1) * 1000
        f.write(f'{note1},{time1},{time2},{diff_ms}\n')
```

Then analyze in Excel/Google Sheets with charts.

### Audio Analysis (Alternative Method)

If MIDI timing looks identical but audio sounds different:

1. **Record audio output** from SWAM:
   - Use Audacity or your DAW to record both playbacks
   - Save as WAV files

2. **Compare waveforms**:
   - Load both WAVs in Audacity
   - Use Analyze → Plot Spectrum to compare frequency content
   - Use Effect → Invert on one track, then mix to hear differences

3. **Programmatic audio comparison** (advanced):
   ```bash
   # Using scipy/numpy
   python -c "
   import numpy as np
   from scipy.io import wavfile
   
   rate1, audio1 = wavfile.read('ableton.wav')
   rate2, audio2 = wavfile.read('webpage.wav')
   
   # Normalize and compare
   diff = np.abs(audio1.astype(float) - audio2.astype(float))
   print(f'Average difference: {np.mean(diff):.2f}')
   print(f'Max difference: {np.max(diff):.2f}')
   "
   ```

## Expected Results

For identical MIDI playback:

- ✅ Note count: Exactly the same
- ✅ Note timing: < 10ms difference (imperceptible)
- ✅ CC message counts: Exactly the same or ±1-2 (rounding)
- ✅ Timing drift: < 100ms over full song (prevents cumulative errors)

If you see these results, the web player is outputting MIDI identically to Ableton Live! 🎯

## Why This Matters

**Use case 1: Confidence in deployment**
- Proves the web player is production-ready
- Shows browser-based MIDI is as accurate as professional DAWs

**Use case 2: Debugging timing issues**
- Identifies where timing errors accumulate
- Helps tune the drift compensation algorithm

**Use case 3: Tempo accuracy verification**
- Confirms tempo changes are handled correctly
- Validates tempo slider multiplier works as expected

## Quick Reference

```bash
# List available MIDI ports
python scripts/record_midi_output.py --list-ports

# Record from specific port for 120 seconds
python scripts/record_midi_output.py --record rec.json --port "loopMIDI Port" --duration 120

# Record until Ctrl+C (for long files)
python scripts/record_midi_output.py --record rec.json

# Compare two recordings
python scripts/record_midi_output.py --compare rec1.json rec2.json
```

## Creating the Recordings Directory

```bash
mkdir recordings
```

Keep your recordings organized with descriptive names:
- `ableton_pala1_120bpm.json`
- `webpage_pala1_120bpm.json`
- `ableton_dpriver_180bpm.json`
- `webpage_dpriver_180bpm.json`
