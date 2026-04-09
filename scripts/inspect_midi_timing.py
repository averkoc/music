"""Inspect MIDI message timing for debugging CC timing issues."""
import mido
import sys

if len(sys.argv) < 2:
    print("Usage: python inspect_midi_timing.py <midi_file>")
    sys.exit(1)

midi_path = sys.argv[1]
mid = mido.MidiFile(midi_path)

print(f"\n{'='*80}")
print(f"MIDI Timing Inspector: {midi_path}")
print(f"{'='*80}\n")

for track in mid.tracks:
    print(f"Track: {track.name}")
    
    # Find first note-on and show 20 messages before/after
    messages = list(track)
    cumulative_time = 0
    
    for i, msg in enumerate(messages):
        cumulative_time += msg.time
        
        if msg.type == 'note_on' and msg.velocity > 0:
            print(f"\n{'='*80}")
            print(f"First Note-On at index {i}, cumulative time {cumulative_time}")
            print(f"{'='*80}")
            
            # Show 10 messages before
            start_idx = max(0, i - 10)
            ct = 0
            for j in range(start_idx):
                ct += messages[j].time
            
            print("\nMessages around first note:")
            print(f"{'Idx':<5} {'Cum.Time':<10} {'Δt':<6} {'Type':<15} {'Details'}")
            print("-" * 80)
            
            for j in range(start_idx, min(len(messages), i + 15)):
                m = messages[j]
                ct += m.time
                details = ""
                if m.type == 'control_change':
                    cc_names = {1: "CC1/Mod", 2: "CC2/Breath", 5: "CC5/Port", 11: "CC11/Expr", 17: "CC17", 64: "CC64/Sust", 74: "CC74/Harmonics"}
                    details = f"{cc_names.get(m.control, f'CC{m.control}')} = {m.value}"
                elif m.type == 'note_on':
                    details = f"Note {m.note}, vel {m.velocity}"
                elif m.type == 'note_off':
                    details = f"Note {m.note}"
                
                marker = " ← NOTE-ON" if j == i else ""
                print(f"{j:<5} {ct:<10} {m.time:<6} {m.type:<15} {details}{marker}")
            
            # Only show first note
            break
    break

print("\n")
