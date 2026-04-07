"""
Check for note overlaps in MIDI file (for glissando verification).
"""
import sys
import mido
from collections import defaultdict

def check_overlaps(midi_path):
    mid = mido.MidiFile(midi_path)
    track = mid.tracks[0]
    
    time = 0
    active_notes = {}  # note -> start_time
    overlaps = []
    cc5_events = []
    
    for msg in track:
        time += msg.time
        
        if msg.type == 'note_on' and msg.velocity > 0:
            # Check if other notes are active
            if active_notes:
                overlapping_notes = list(active_notes.keys())
                overlaps.append({
                    'time': time,
                    'new_note': msg.note,
                    'overlapping_with': overlapping_notes
                })
            active_notes[msg.note] = time
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active_notes:
                del active_notes[msg.note]
        elif msg.type == 'control_change' and msg.control == 5:  # CC5 portamento
            cc5_events.append({'time': time, 'value': msg.value})
    
    print(f"MIDI File: {midi_path}")
    print(f"\n{'='*60}")
    print(f"CC5 (Portamento) Events: {len(cc5_events)}")
    for evt in cc5_events:
        print(f"  Time {evt['time']:6d}: CC5 = {evt['value']}")
    
    print(f"\n{'='*60}")
    print(f"Note Overlaps Detected: {len(overlaps)}")
    for overlap in overlaps:
        print(f"  Time {overlap['time']:6d}: Note {overlap['new_note']} starts "
              f"while {overlap['overlapping_with']} still playing")
    
    print(f"\n{'='*60}")
    if cc5_events and overlaps:
        print("✓ Glissando implementation looks CORRECT:")
        print(f"  - {len(cc5_events)} CC5 portamento events")
        print(f"  - {len(overlaps)} note overlaps for pitch glide")
    elif cc5_events:
        print("⚠ CC5 events found but no note overlaps")
        print("  Glissando may not work without overlap!")
    else:
        print("ℹ No glissando events detected")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_glissando_overlap.py <midi_file>")
        sys.exit(1)
    
    check_overlaps(sys.argv[1])
