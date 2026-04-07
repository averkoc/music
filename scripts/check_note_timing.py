"""Check note timing and rhythm in generated MIDI."""
import mido
import sys

def analyze_timing(filename):
    """Analyze note timing to detect rhythm issues."""
    mid = mido.MidiFile(filename)
    track = mid.tracks[0]
    
    current_time = 0
    notes = []  # (note, on_time, off_time, duration)
    active_notes = {}  # note -> on_time
    
    print(f"\n{'='*80}")
    print(f"TIMING ANALYSIS: {filename}")
    print(f"{'='*80}\n")
    print(f"Ticks per beat: {mid.ticks_per_beat}")
    
    for msg in track:
        current_time += msg.time
        
        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes[msg.note] = current_time
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active_notes:
                on_time = active_notes[msg.note]
                duration = current_time - on_time
                notes.append((msg.note, on_time, current_time, duration))
                del active_notes[msg.note]
    
    # Check for rhythm issues
    print("\nFIRST 20 NOTES (timing check):")
    print("-" * 80)
    print(f"{'Note':<8} {'On (ticks)':<12} {'Duration':<12} {'Gap to Next':<15}")
    print("-" * 80)
    
    for i, (note, on_time, off_time, duration) in enumerate(notes[:20]):
        pitch_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note % 12]
        octave = note // 12 - 1
        
        # Check gap to next note
        gap = ""
        if i + 1 < len(notes):
            next_on = notes[i + 1][1]
            gap_ticks = next_on - on_time
            gap = f"{gap_ticks} ticks"
            
            # Flag if gap seems wrong
            if gap_ticks > duration + 100:  # More than 100 ticks gap after note ends
                gap += " ⚠️ DETACHED"
        
        print(f"{pitch_name}{octave:<6} {on_time:<12} {duration:<12} {gap}")
    
    # Check for consistent note spacing
    print("\n" + "="*80)
    print("RHYTHM CONSISTENCY CHECK")
    print("="*80)
    
    gaps = []
    for i in range(len(notes) - 1):
        gap = notes[i+1][1] - notes[i][1]  # Time between note onsets
        gaps.append(gap)
    
    if gaps:
        from collections import Counter
        gap_counts = Counter(gaps)
        print(f"\nMost common gaps between note onsets:")
        for gap, count in gap_counts.most_common(5):
            beats = gap / mid.ticks_per_beat
            print(f"  {gap:4d} ticks ({beats:.2f} beats): {count:2d} times")
        
        # Check for unusual gaps
        avg_gap = sum(gaps) / len(gaps)
        large_gaps = [g for g in gaps if g > avg_gap * 2]
        
        if large_gaps:
            print(f"\n⚠️  WARNING: Found {len(large_gaps)} unusually large gaps (> 2x average)")
            print(f"  Average gap: {avg_gap:.1f} ticks")
            print(f"  Large gaps: {large_gaps[:5]}")
        else:
            print(f"\n✓ No unusual timing gaps detected")
            print(f"  Average onset spacing: {avg_gap:.1f} ticks ({avg_gap/mid.ticks_per_beat:.2f} beats)")
    
    # Check note durations
    durations = [n[3] for n in notes]
    avg_duration = sum(durations) / len(durations)
    print(f"\n✓ Average note duration: {avg_duration:.1f} ticks ({avg_duration/mid.ticks_per_beat:.2f} beats)")
    
    # Check for overlaps
    overlaps = 0
    for i in range(len(notes) - 1):
        if notes[i][2] > notes[i+1][1]:  # Current note ends after next starts
            overlaps += 1
    
    print(f"✓ Note overlaps (legato): {overlaps}/{len(notes)-1}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_timing(sys.argv[1])
    else:
        # Test both files
        print("COMPARING TIMING:")
        analyze_timing('midi_output/test_rhythm_fixed.mid')
