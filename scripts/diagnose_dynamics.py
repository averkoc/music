"""Diagnose dynamic detection issues in violintest.xml"""
from music21 import converter
from articulation_detector import MusicXMLArticulationDetector, DynamicLevel
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else 'musescore_files/violintest.xml'

print("=" * 80)
print(f"DYNAMIC DETECTION DIAGNOSTIC: {filename}")
print("=" * 80)

# Load score
score = converter.parse(filename)
part = score.parts[0]

# Check for dynamics in the raw MusicXML
print("\n1. RAW DYNAMICS IN MUSICXML:")
print("-" * 80)
from music21 import dynamics
all_dynamics = part.flatten().getElementsByClass(dynamics.Dynamic)
print(f"   Total dynamic markings found: {len(all_dynamics)}")

for dyn in all_dynamics:
    offset = dyn.offset
    value = dyn.value if hasattr(dyn, 'value') else str(dyn)
    print(f"   Offset {offset:6.2f}: {value}")

# Check what the detector extracts
print("\n2. DETECTOR ANALYSIS:")
print("-" * 80)
detector = MusicXMLArticulationDetector()
note_articulations, dynamic_changes = detector.analyze_score(score)

print(f"   Notes analyzed: {len(note_articulations)}")
print(f"   Dynamic changes detected: {len(dynamic_changes)}")

# Show dynamics assigned to each note
print("\n3. DYNAMICS ASSIGNED TO NOTES:")
print("-" * 80)
print(f"{'Note':<6} {'Offset':<8} {'Pitch':<6} {'Dynamic':<8} {'CC11':<6} {'Velocity':<8}")
print("-" * 80)

prev_dynamic = None
for i, note in enumerate(note_articulations[:30]):  # First 30 notes
    pitch_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note.pitch % 12]
    octave = note.pitch // 12 - 1
    
    dynamic_str = note.dynamic_level.marking if note.dynamic_level else "None"
    cc11 = note.dynamic_level.cc_value if note.dynamic_level else "N/A"
    
    # Highlight dynamic changes
    marker = ""
    if note.dynamic_level != prev_dynamic:
        marker = " ← CHANGE"
    prev_dynamic = note.dynamic_level
    
    print(f"{i+1:<6} {note.onset_time:<8.2f} {pitch_name}{octave:<4} {dynamic_str:<8} {cc11!s:<6} {note.velocity:<8}{marker}")

# Check if dynamics are at the RIGHT offsets
print("\n4. DYNAMICS VS NOTE TIMING:")
print("-" * 80)
print("   Checking if dynamics are placed correctly in the score...")

for dyn in all_dynamics:
    notes_at_offset = [n for n in note_articulations if abs(n.onset_time - dyn.offset) < 0.1]
    dyn_value = dyn.value if hasattr(dyn, 'value') else str(dyn)
    
    if notes_at_offset:
        print(f"   ✓ Dynamic '{dyn_value}' at {dyn.offset:.2f} -> {len(notes_at_offset)} note(s)")
    else:
        print(f"   ⚠ Dynamic '{dyn_value}' at {dyn.offset:.2f} -> NO NOTES FOUND")
        # Find nearest note
        nearest = min(note_articulations, key=lambda n: abs(n.onset_time - dyn.offset))
        print(f"      Nearest note is at {nearest.onset_time:.2f} (gap: {abs(nearest.onset_time - dyn.offset):.2f})")

print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY:")
print("=" * 80)

# Check if dynamics are being applied
unique_dynamics = set(n.dynamic_level for n in note_articulations if n.dynamic_level)
if len(unique_dynamics) > 1:
    print("✓ Multiple dynamic levels detected:")
    for dyn in sorted(unique_dynamics, key=lambda d: d.cc_value):
        count = sum(1 for n in note_articulations if n.dynamic_level == dyn)
        print(f"  - {dyn.marking}: {count} notes (CC11={dyn.cc_value})")
elif len(unique_dynamics) == 1:
    dyn = list(unique_dynamics)[0]
    print(f"⚠ Only ONE dynamic level found: {dyn.marking} (CC11={dyn.cc_value})")
    print(f"  All {len(note_articulations)} notes have the same dynamic")
    print(f"  This suggests dynamics aren't being detected or applied correctly")
else:
    print("❌ NO dynamics detected on any notes!")
    print("  This is a serious issue - all notes should have at least a default dynamic")

print("=" * 80)
