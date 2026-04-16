#!/usr/bin/env python3
"""
Playback Timing Verifier (No C++ Required!)

Alternative to MIDI recording that works without python-rtmidi.
Verifies timing accuracy by analyzing the MIDI file and server logs.

This approach is actually better because:
1. No C++ compiler needed
2. Verifies the source of truth (MIDI file timing)
3. Uses server's built-in timing verification
4. Can detect timing issues before they reach SWAM

Usage:
    # Analyze a MIDI file's expected timing
    python verify_playback_timing.py midi_output/pala1_violin_swam.mid
    
    # Then check server logs after playing it in the web player
    # Server will show: "⏱️  Timing: X.XXs actual vs X.XXs expected (error: X.XXXs)"
"""

import sys
import mido
from pathlib import Path
from collections import defaultdict


def analyze_midi_timing(filepath: Path):
    """
    Analyze MIDI file to calculate expected playback timing
    """
    print("\n" + "="*80)
    print(f"MIDI TIMING ANALYSIS: {filepath.name}")
    print("="*80)
    
    mid = mido.MidiFile(filepath)
    
    # Extract tempo map
    tempo_map = []
    for track in mid.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            if msg.type == 'set_tempo':
                tempo_map.append((abs_time, msg.tempo))
    
    tempo_map.sort(key=lambda x: x[0])
    
    if not tempo_map:
        tempo_map.append((0, 500000))  # Default 120 BPM
    
    print(f"\n📁 File Info:")
    print(f"   Format: Type {mid.type}")
    print(f"   Tracks: {len(mid.tracks)}")
    print(f"   Ticks per beat: {mid.ticks_per_beat}")
    
    # Show tempo information
    print(f"\n🎵 Tempo Information:")
    if len(tempo_map) == 1:
        bpm = mido.tempo2bpm(tempo_map[0][1])
        print(f"   Single tempo: {bpm:.1f} BPM")
    else:
        print(f"   {len(tempo_map)} tempo changes detected:")
        for tick, tempo in tempo_map[:5]:  # Show first 5
            bpm = mido.tempo2bpm(tempo)
            seconds = mido.tick2second(tick, mid.ticks_per_beat, tempo_map[0][1])
            print(f"      At {seconds:.1f}s (tick {tick}): {bpm:.1f} BPM")
        if len(tempo_map) > 5:
            print(f"      ... and {len(tempo_map) - 5} more")
    
    # Calculate total duration
    all_events = []
    for track in mid.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            if not msg.is_meta:
                all_events.append(abs_time)
    
    if not all_events:
        print("\n⚠️  No MIDI events found!")
        return
    
    last_event_tick = max(all_events)
    
    # Calculate duration accounting for tempo changes
    total_duration = 0.0
    prev_tick = 0
    tempo_index = 0
    current_tempo = tempo_map[0][1]
    
    for i in range(len(tempo_map)):
        if i < len(tempo_map) - 1:
            segment_end = tempo_map[i + 1][0]
        else:
            segment_end = last_event_tick
        
        delta_ticks = segment_end - prev_tick
        segment_duration = mido.tick2second(delta_ticks, mid.ticks_per_beat, current_tempo)
        total_duration += segment_duration
        
        prev_tick = segment_end
        if i + 1 < len(tempo_map):
            current_tempo = tempo_map[i + 1][1]
    
    print(f"\n⏱️  Expected Duration: {total_duration:.2f} seconds ({total_duration/60:.1f} minutes)")
    
    # Count message types
    note_count = 0
    cc_counts = defaultdict(int)
    
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'note_on':
                note_count += 1
            elif msg.type == 'control_change':
                cc_counts[msg.control] += 1
    
    print(f"\n📊 Event Statistics:")
    print(f"   Note events: {note_count}")
    print(f"   CC messages: {sum(cc_counts.values())}")
    
    if cc_counts:
        cc_names = {
            1: "CC1 (Vibrato Depth)",
            2: "CC2 (Breath)",
            5: "CC5 (Portamento)",
            11: "CC11 (Expression)",
            17: "CC17 (Vibrato Rate)",
            20: "CC20 (Harmonics)",
            21: "CC21 (Brightness Offset)",
            64: "CC64 (Sustain)",
            74: "CC74 (Brightness)"
        }
        
        print(f"\n   CC Breakdown:")
        for cc, count in sorted(cc_counts.items()):
            name = cc_names.get(cc, f"CC{cc}")
            print(f"      {name}: {count} messages")
    
    # Timing accuracy thresholds
    print("\n" + "="*80)
    print("TIMING ACCURACY VERIFICATION")
    print("="*80)
    print(f"""
When you play this file in the web player, check the server logs for:

   ⏱️  Timing: X.XXs actual vs {total_duration:.2f}s expected (error: X.XXXs)

✅ EXCELLENT: Error < 0.100s  (sub-100ms accuracy)
✓  GOOD:      Error < 0.500s  (half-second tolerance)
⚠️  WARNING:   Error > 1.000s  (needs investigation)

Expected total duration: {total_duration:.2f}s
At 100% tempo: {total_duration:.2f}s
At 150% tempo: {total_duration/1.5:.2f}s
At 50% tempo:  {total_duration*2:.2f}s
""")
    
    # Calculate expected timing at different percentages
    print("="*80)
    print("TEMPO SCALING REFERENCE")
    print("="*80)
    print(f"\n{'Slider %':<12} {'Expected Duration':<20} {'Use Case'}")
    print("-"*80)
    
    tempo_settings = [
        (50, "Practice (half speed)"),
        (75, "Learning"),
        (100, "Normal playback"),
        (125, "Faster practice"),
        (150, "Quick preview"),
        (200, "Double speed scan")
    ]
    
    for pct, use_case in tempo_settings:
        duration_at_pct = total_duration / (pct / 100)
        print(f"{pct}%{'':<9} {duration_at_pct:.2f}s{'':<15} {use_case}")
    
    print("\n" + "="*80)
    print("HOW TO VERIFY")
    print("="*80)
    print(f"""
1. Start the web player server:
   python scripts/midi_websocket_server.py

2. Open http://localhost:8000/swam_violin_player_v2.html

3. Load this file: {filepath.name}

4. Click Play and let it complete

5. Check the server terminal for timing report:
   ✅ Playback complete (XXX events sent)
   ⏱️  Timing: X.XXs actual vs {total_duration:.2f}s expected (error: X.XXXs)

6. If error < 0.1s: PERFECT! ✅
   If error < 0.5s: Good, acceptable
   If error > 1.0s: Check for issues

This verifies the web player's timing accuracy without needing
to record MIDI output or compare with Ableton Live!
""")


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_playback_timing.py <midi_file>")
        print("\nExample:")
        print("  python verify_playback_timing.py midi_output/pala1_violin_swam.mid")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    
    if not filepath.suffix.lower() in ['.mid', '.midi']:
        print(f"❌ Not a MIDI file: {filepath}")
        sys.exit(1)
    
    analyze_midi_timing(filepath)


if __name__ == "__main__":
    main()
