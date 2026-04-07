"""
MIDI CC Inspector

Analyze CC messages in a MIDI file to see what's actually being sent.
"""

import sys
import mido
from collections import defaultdict
from pathlib import Path


def inspect_midi_ccs(midi_path: Path):
    """Inspect and report on CC messages in a MIDI file."""
    
    midi_file = mido.MidiFile(midi_path)
    
    print(f"\n{'='*60}")
    print(f"MIDI CC Inspector: {midi_path.name}")
    print(f"{'='*60}\n")
    
    # Track CC statistics
    cc_stats = defaultdict(lambda: {'count': 0, 'values': [], 'min': 127, 'max': 0})
    note_count = 0
    total_messages = 0
    
    for track_num, track in enumerate(midi_file.tracks):
        print(f"Track {track_num}: {track.name if hasattr(track, 'name') else 'Unnamed'}")
        
        for msg in track:
            total_messages += 1
            
            if msg.type == 'note_on' and msg.velocity > 0:
                note_count += 1
            
            elif msg.type == 'control_change':
                cc_num = msg.control
                cc_val = msg.value
                
                cc_stats[cc_num]['count'] += 1
                cc_stats[cc_num]['values'].append(cc_val)
                cc_stats[cc_num]['min'] = min(cc_stats[cc_num]['min'], cc_val)
                cc_stats[cc_num]['max'] = max(cc_stats[cc_num]['max'], cc_val)
    
    print(f"\nTotal messages: {total_messages}")
    print(f"Note events: {note_count}")
    print(f"\n{'='*60}")
    print("CC MESSAGE SUMMARY")
    print(f"{'='*60}\n")
    
    if not cc_stats:
        print("❌ NO CC MESSAGES FOUND IN FILE!")
        return
    
    # CC name mapping
    cc_names = {
        1: "Modulation (Vibrato)",
        2: "Breath",
        11: "Expression (Dynamics)",
        64: "Sustain/Legato",
        74: "Brightness/Filter",
        91: "Reverb"
    }
    
    for cc_num in sorted(cc_stats.keys()):
        stats = cc_stats[cc_num]
        cc_name = cc_names.get(cc_num, f"CC{cc_num}")
        
        print(f"\n📊 CC{cc_num}: {cc_name}")
        print(f"   Count: {stats['count']} messages")
        print(f"   Range: {stats['min']} - {stats['max']}")
        print(f"   Variation: {stats['max'] - stats['min']} units")
        
        # Calculate distribution
        values = stats['values']
        avg = sum(values) / len(values)
        print(f"   Average: {avg:.1f}")
        
        # Check if values are too similar
        if stats['max'] - stats['min'] < 10:
            print(f"   ⚠️  WARNING: Very low variation! Might appear 'still' in DAW")
        
        # Show value distribution
        unique_values = sorted(set(values))
        if len(unique_values) <= 10:
            print(f"   Unique values: {unique_values}")
        else:
            print(f"   Unique values: {len(unique_values)} different values")
    
    print(f"\n{'='*60}")
    print("INTERPRETATION")
    print(f"{'='*60}\n")
    
    # Provide interpretation
    if 11 not in cc_stats:
        print("❌ CC11 (Expression) NOT FOUND - Dynamics won't work!")
    else:
        cc11_range = cc_stats[11]['max'] - cc_stats[11]['min']
        if cc11_range < 10:
            print(f"⚠️  CC11 range is only {cc11_range} - very subtle dynamics")
        elif cc11_range < 30:
            print(f"✓ CC11 range is {cc11_range} - moderate dynamics")
        else:
            print(f"✓✓ CC11 range is {cc11_range} - good dynamic range!")
    
    if 1 in cc_stats:
        if cc_stats[1]['max'] == 0:
            print("⚠️  CC1 (Vibrato) is all zeros - no vibrato")
        else:
            print(f"✓ CC1 (Vibrato) present: 0-{cc_stats[1]['max']}")
    
    if 74 in cc_stats:
        cc74_range = cc_stats[74]['max'] - cc_stats[74]['min']
        if cc74_range < 5:
            print(f"⚠️  CC74 (Brightness) barely changes ({cc74_range} units)")
        else:
            print(f"✓ CC74 (Brightness) varies by {cc74_range} units")
    
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python inspect_midi_ccs.py <midi_file.mid>")
        sys.exit(1)
    
    midi_path = Path(sys.argv[1])
    
    if not midi_path.exists():
        print(f"Error: File not found: {midi_path}")
        sys.exit(1)
    
    inspect_midi_ccs(midi_path)


if __name__ == "__main__":
    main()
