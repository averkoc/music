"""Compare timing between reference MIDI and current version."""
import mido
import sys
from pathlib import Path

def extract_notes(filename):
    """Extract note timing data from MIDI file."""
    mid = mido.MidiFile(filename)
    track = mid.tracks[0]
    
    current_time = 0
    notes = []  # (note, on_time, velocity, duration)
    active_notes = {}
    
    for msg in track:
        current_time += msg.time
        
        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes[msg.note] = (current_time, msg.velocity)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active_notes:
                on_time, velocity = active_notes[msg.note]
                duration = current_time - on_time
                notes.append((msg.note, on_time, velocity, duration))
                del active_notes[msg.note]
    
    return notes, mid.ticks_per_beat

def compare_timing(ref_file, check_file):
    """Compare timing between reference and file to check."""
    print("=" * 80)
    print("MIDI TIMING COMPARISON")
    print("=" * 80)
    
    ref_notes, ref_tpb = extract_notes(ref_file)
    check_notes, check_tpb = extract_notes(check_file)
    
    print(f"\nReference: {ref_file}")
    print(f"  Notes: {len(ref_notes)}")
    print(f"  Ticks per beat: {ref_tpb}")
    
    print(f"\nTo Check: {check_file}")
    print(f"  Notes: {len(check_notes)}")
    print(f"  Ticks per beat: {check_tpb}")
    
    # Compare note counts
    if len(ref_notes) != len(check_notes):
        print(f"\n⚠️  WARNING: Different number of notes!")
        print(f"  Reference: {len(ref_notes)} notes")
        print(f"  Check: {len(check_notes)} notes")
        return
    
    # Compare timing for first 30 notes
    print("\n" + "=" * 80)
    print("TIMING COMPARISON (First 30 notes)")
    print("=" * 80)
    print(f"{'Note':<8} {'Ref Onset':<12} {'Check Onset':<12} {'Difference':<15} {'Status'}")
    print("-" * 80)
    
    timing_issues = 0
    max_diff = 0
    
    for i in range(min(30, len(ref_notes))):
        ref_note, ref_on, ref_vel, ref_dur = ref_notes[i]
        check_note, check_on, check_vel, check_dur = check_notes[i]
        
        pitch_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][ref_note % 12]
        octave = ref_note // 12 - 1
        
        diff = check_on - ref_on
        max_diff = max(max_diff, abs(diff))
        
        if ref_note != check_note:
            status = "⚠️  WRONG NOTE"
            timing_issues += 1
        elif abs(diff) > 10:  # More than 10 ticks difference
            status = "⚠️  TIMING OFF"
            timing_issues += 1
        elif abs(diff) > 0:
            status = "~OK (slight)"
        else:
            status = "✓ PERFECT"
        
        print(f"{pitch_name}{octave:<6} {ref_on:<12} {check_on:<12} {diff:+4d} ticks      {status}")
    
    # Overall statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Calculate onset gaps
    ref_gaps = [ref_notes[i+1][1] - ref_notes[i][1] for i in range(len(ref_notes)-1)]
    check_gaps = [check_notes[i+1][1] - check_notes[i][1] for i in range(len(check_notes)-1)]
    
    avg_ref_gap = sum(ref_gaps) / len(ref_gaps)
    avg_check_gap = sum(check_gaps) / len(check_gaps)
    
    print(f"\nReference average note spacing: {avg_ref_gap:.1f} ticks ({avg_ref_gap/ref_tpb:.2f} beats)")
    print(f"Check average note spacing:     {avg_check_gap:.1f} ticks ({avg_check_gap/check_tpb:.2f} beats)")
    print(f"Difference: {avg_check_gap - avg_ref_gap:+.1f} ticks")
    
    if timing_issues > 0:
        print(f"\n⚠️  Found {timing_issues} timing issues in first 30 notes")
        print(f"   Maximum timing difference: {max_diff} ticks")
    else:
        print(f"\n✓ All notes match within 10 ticks tolerance!")
        if max_diff > 0:
            print(f"  Maximum difference: {max_diff} ticks (acceptable)")
        else:
            print(f"  Perfect match - all notes at identical positions!")
    
    # Check for pattern of increasing delays
    if len(ref_notes) >= 10:
        early_diffs = [check_notes[i][1] - ref_notes[i][1] for i in range(5)]
        late_diffs = [check_notes[i][1] - ref_notes[i][1] for i in range(len(ref_notes)-5, len(ref_notes))]
        
        avg_early = sum(early_diffs) / len(early_diffs)
        avg_late = sum(late_diffs) / len(late_diffs)
        
        if abs(avg_late - avg_early) > 50:
            print(f"\n⚠️  PROGRESSIVE TIMING DRIFT DETECTED!")
            print(f"   Early notes: {avg_early:+.1f} ticks average difference")
            print(f"   Late notes:  {avg_late:+.1f} ticks average difference")
            print(f"   This suggests cumulative timing errors (like vibrato delays)")

if __name__ == "__main__":
    ref_file = "midi_output/reference.mid"
    check_file = "midi_output/tobechecked.mid"
    
    if len(sys.argv) > 2:
        ref_file = sys.argv[1]
        check_file = sys.argv[2]
    
    ref_path = Path(ref_file)
    check_path = Path(check_file)
    
    if not ref_path.exists():
        print(f"❌ Reference file not found: {ref_file}")
        print(f"   Please save reference.mid to midi_output/")
        sys.exit(1)
    
    if not check_path.exists():
        print(f"❌ Check file not found: {check_file}")
        print(f"   Please save tobechecked.mid to midi_output/")
        sys.exit(1)
    
    compare_timing(ref_file, check_file)
