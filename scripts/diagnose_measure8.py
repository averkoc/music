"""Inspect measure 8 specifically to check dynamic wedges (hairpins)."""
from music21 import converter
from articulation_detector import MusicXMLArticulationDetector
import mido

score = converter.parse('musescore_files/violintest.xml')
part = score.parts[0]

print("=" * 80)
print("MEASURE 8 ANALYSIS: DYNAMICS & HAIRPINS")
print("=" * 80)

# Get measure 8
measures = part.getElementsByClass('Measure')
measure_8 = None
for m in measures:
    if m.measureNumber == 8:
        measure_8 = m
        break

if measure_8:
    print(f"\nMeasure 8 found at offset {measure_8.offset}")
    print(f"Duration: {measure_8.quarterLength} quarter notes")
    
    # Get notes in measure 8
    notes_m8 = list(measure_8.notes)
    print(f"\nNotes in measure 8: {len(notes_m8)}")
    for n in notes_m8:
        pitch_name = n.pitch.nameWithOctave if hasattr(n, 'pitch') else 'Rest'
        print(f"  {pitch_name} at offset {n.offset} (global: {measure_8.offset + n.offset})")

# Check for crescendo/diminuendo spanners around measure 8
print("\n" + "=" * 80)
print("CRESCENDO/DIMINUENDO WEDGES (HAIRPINS) IN ENTIRE SCORE:")
print("=" * 80)

from music21 import dynamics

# Find all dynamic wedges
crescendos = part.flatten().getElementsByClass('Crescendo')
diminuendos = part.flatten().getElementsByClass('Diminuendo')

print(f"\nCrescendos found: {len(crescendos)}")
for i, cresc in enumerate(crescendos):
    start = cresc.getFirst().offset if cresc.getFirst() else 'N/A'
    end = cresc.getLast().offset if cresc.getLast() else 'N/A'
    print(f"  Crescendo {i+1}: offset {start} → {end}")
    
    # Check for dynamics at start/end
    if start != 'N/A':
        dyns_at_start = part.flatten().getElementsByOffset(start, start + 0.1, classList=[dynamics.Dynamic])
        if dyns_at_start:
            print(f"    Start dynamic: {dyns_at_start[0].value if hasattr(dyns_at_start[0], 'value') else dyns_at_start[0]}")
        else:
            print(f"    ⚠ NO dynamic marking at start")
    
    if end != 'N/A':
        dyns_at_end = part.flatten().getElementsByOffset(end - 0.1, end + 0.1, classList=[dynamics.Dynamic])
        if dyns_at_end:
            print(f"    End dynamic: {dyns_at_end[0].value if hasattr(dyns_at_end[0], 'value') else dyns_at_end[0]}")
        else:
            print(f"    ⚠ NO dynamic marking at end (will be estimated)")

print(f"\nDiminuendos found: {len(diminuendos)}")
for i, dim in enumerate(diminuendos):
    start = dim.getFirst().offset if dim.getFirst() else 'N/A'
    end = dim.getLast().offset if dim.getLast() else 'N/A'
    
    # Check which measure this is in
    measure_num = "?"
    if start != 'N/A':
        for m in measures:
            if m.offset <= start < m.offset + m.quarterLength:
                measure_num = m.measureNumber
                break
    
    print(f"  Diminuendo {i+1}: offset {start} → {end} (measure ~{measure_num})")
    
    # Check for dynamics at start/end
    if start != 'N/A':
        dyns_at_start = part.flatten().getElementsByOffset(start - 0.1, start + 0.1, classList=[dynamics.Dynamic])
        if dyns_at_start:
            print(f"    Start dynamic: {dyns_at_start[0].value if hasattr(dyns_at_start[0], 'value') else dyns_at_start[0]}")
        else:
            print(f"    ⚠ NO dynamic marking at start")
    
    if end != 'N/A':
        dyns_at_end = part.flatten().getElementsByOffset(end - 0.1, end + 0.1, classList=[dynamics.Dynamic])
        if dyns_at_end:
            print(f"    End dynamic: {dyns_at_end[0].value if hasattr(dyns_at_end[0], 'value') else dyns_at_end[0]}")
        else:
            print(f"    ⚠ NO dynamic marking at end (will be estimated)")

# Check what the detector does with these
print("\n" + "=" * 80)
print("DETECTED DYNAMIC CHANGES (from articulation_detector):")
print("=" * 80)

detector = MusicXMLArticulationDetector()
note_articulations, dynamic_changes = detector.analyze_score(score)

print(f"\nDynamic changes detected: {len(dynamic_changes)}")
for dc in dynamic_changes:
    change_type = "CRESCENDO" if dc.is_crescendo else "DIMINUENDO"
    print(f"\n{change_type}:")
    print(f"  Time: {dc.start_time} → {dc.end_time}")
    print(f"  Dynamic: {dc.start_dynamic.marking} ({dc.start_dynamic.cc_value}) → {dc.end_dynamic.marking} ({dc.end_dynamic.cc_value})")
    
    # Check which measure this is in
    start_measure = None
    end_measure = None
    for m in measures:
        if m.offset <= dc.start_time < m.offset + m.quarterLength:
            start_measure = m.measureNumber
        if m.offset <= dc.end_time < m.offset + m.quarterLength:
            end_measure = m.measureNumber
    print(f"  Measures: {start_measure} → {end_measure}")

# Check if dynamic changes are actually applied to the MIDI
print("\n" + "=" * 80)
print("CHECKING MIDI OUTPUT FOR DYNAMIC WEDGES:")
print("=" * 80)

mid = mido.MidiFile('midi_output/violintest_violin_swam.mid')
track = mid.tracks[0]

# The _add_dynamic_changes method should insert CC11 ramps
# Let's see if there are CC11 messages NOT tied to note onsets
cc11_messages = []
cumulative_time = 0
for msg in track:
    cumulative_time += msg.time
    if msg.type == 'control_change' and msg.control == 11:
        cc11_messages.append((cumulative_time, msg.value))

print(f"\nTotal CC11 messages: {len(cc11_messages)}")
print("\nFirst 20 CC11 messages:")
for i, (time, value) in enumerate(cc11_messages[:20]):
    beats = time / 480  # 480 ticks per beat
    print(f"  {i+1:3}. Time {time:6} ticks ({beats:6.2f} beats): CC11={value}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("\nIf diminuendo is not working in measure 8:")
print("1. Check if there's a dynamic marking at the END of the hairpin")
print("2. Without an end dynamic, the code ESTIMATES the target (±2-3 levels)")
print("3. The estimation might not match your musical intention")
print("\nRECOMMENDATION:")
print("  Add explicit dynamic markings (mp, mf, f, etc.) at the end of hairpins")
print("  This gives the converter exact targets instead of guessing")
print("=" * 80)
