"""Test script to check what measure and beat information is available from MusicXML."""
from music21 import converter

# Load a MusicXML file
score = converter.parse('musescore_files/pala1.mxl')
part = score.parts[0]

print("=" * 80)
print("MEASURE AND BEAT INFORMATION AVAILABLE IN MUSICXML")
print("=" * 80)

# Check time signatures
print("\n1. TIME SIGNATURES:")
time_sigs = part.flatten().getElementsByClass('TimeSignature')
for ts in time_sigs:
    print(f"   Offset {ts.offset}: {ts.numerator}/{ts.denominator}")

# Check measures (non-flattened)
print("\n2. MEASURES:")
measures = part.getElementsByClass('Measure')
print(f"   Total measures: {len(measures)}")
if len(measures) > 0:
    print(f"   First measure number: {measures[0].measureNumber}")
    print(f"   Example measure attributes: {dir(measures[0])[:10]}...")

# Check beat strength on notes
print("\n3. BEAT STRENGTH (first 15 notes):")
print(f"   {'Note':<8} {'Offset':<10} {'Beat':<8} {'BeatStr':<10} {'Measure':<10}")
print("   " + "-" * 60)

note_count = 0
for measure in measures[:5]:  # First 5 measures
    for note in measure.notes:
        if note_count >= 15:
            break
        
        # Get beat strength (0.0 = weakest, 1.0 = strongest/downbeat)
        beat_strength = note.beatStrength if hasattr(note, 'beatStrength') else 'N/A'
        beat = note.beat if hasattr(note, 'beat') else 'N/A'
        
        pitch_name = note.pitch.nameWithOctave if hasattr(note, 'pitch') else 'Rest'
        
        print(f"   {pitch_name:<8} {note.offset:<10.2f} {beat!s:<8} {beat_strength!s:<10} {measure.measureNumber:<10}")
        note_count += 1
    
    if note_count >= 15:
        break

print("\n4. ACCESSING CONTEXT:")
# Show how to get metrical position
first_note = part.flatten().notes[0]
print(f"   First note pitch: {first_note.pitch.nameWithOctave}")
print(f"   Beat strength: {first_note.beatStrength}")
print(f"   Beat: {first_note.beat}")
print(f"   Offset in measure: {first_note.offset}")

# Check if we can get measure from context
if hasattr(first_note, 'measureNumber'):
    print(f"   Measure number: {first_note.measureNumber}")
else:
    # Try to get it from activeSite
    if hasattr(first_note, 'activeSite') and first_note.activeSite:
        if hasattr(first_note.activeSite, 'measureNumber'):
            print(f"   Measure number (from activeSite): {first_note.activeSite.measureNumber}")

print("\n5. BEAT STRENGTH VALUES:")
print("   In music21:")
print("   - 1.0 = Downbeat (beat 1)")
print("   - 0.5 = Medium strong beat (beat 3 in 4/4)")
print("   - 0.25 = Weak beat (beats 2, 4 in 4/4)")
print("   - Lower = Offbeats, syncopations")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("YES! MusicXML contains beatStrength information that can be used")
print("to emphasize downbeats and strong beats automatically.")
print("=" * 80)
