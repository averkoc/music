"""
Check if vibrato spanner range includes all notes
"""
from music21 import converter

score = converter.parse('musescore_files/violin_reference_test.xml')
part = score.parts[0]

# Find the vibrato spanner
vibrato_ranges = []
for spanner in part.flatten().spanners:
    spanner_name = spanner.__class__.__name__.lower()
    if any(keyword in spanner_name for keyword in ['wavyline', 'trill', 'tremolo']):
        if spanner.getFirst() and spanner.getLast():
            start_offset = spanner.getFirst().offset
            last_note = spanner.getLast()
            end_offset = last_note.offset + last_note.duration.quarterLength
            vibrato_ranges.append((start_offset, end_offset))
            print(f"Vibrato range: {start_offset} to {end_offset}")
            print(f"  First note: offset={spanner.getFirst().offset}, duration={spanner.getFirst().duration.quarterLength}")
            print(f"  Last note: offset={last_note.offset}, duration={last_note.duration.quarterLength}")

# Find all notes in measures 8-9
print("\nNotes in measures 8-9:")
for element in part.flatten().notesAndRests:
    if hasattr(element, 'measureNumber') and element.measureNumber in [8, 9]:
        if hasattr(element, 'pitch'):
            in_range = False
            for start, end in vibrato_ranges:
                if start <= element.offset < end:
                    in_range = True
                    break
            
            status = "✓ IN RANGE" if in_range else "✗ NOT IN RANGE"
            print(f"  M{element.measureNumber}: {element.pitch.nameWithOctave}, offset={element.offset}, duration={element.duration.quarterLength} -> {status}")
