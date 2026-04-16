"""
Quick debug script to see what music21 parses for measure 8
"""
from music21 import converter

score = converter.parse('musescore_files/violin_reference_test.xml')
part = score.parts[0]

print("=" * 60)
print("MEASURE 8 ANALYSIS")
print("=" * 60)

for element in part.flatten().notesAndRests:
    if hasattr(element, 'measureNumber') and element.measureNumber == 8:
        print(f"\nElement: {element}")
        print(f"  Offset: {element.offset}")
        print(f"  Duration: {element.duration.quarterLength} quarters")
        print(f"  Type: {element.duration.type}")
        
        if hasattr(element, 'pitch'):
            print(f"  Pitch: {element.pitch.nameWithOctave} (MIDI {element.pitch.midi})")
        
        # Check for ornaments
        if hasattr(element, 'expressions'):
            print(f" Expressions: {element.expressions}")
        if hasattr(element, 'articulations'):
            print(f"  Articulations: {element.articulations}")
        
        # Check spanners
        spanners = element.getSpannerSites()
        if spanners:
            print(f"  Spanners: {[s.__class__.__name__ for s in spanners]}")

print("\n" + "=" * 60)
print("ALL SPANNERS IN PART")
print("=" * 60)
for spanner in part.flatten().spanners:
    print(f"\n{spanner.__class__.__name__}:")
    if hasattr(spanner, 'getFirst') and hasattr(spanner, 'getLast'):
        first = spanner.getFirst()
        last = spanner.getLast()
        if first and last:
            print(f"  Start: offset {first.offset}, measure {getattr(first, 'measureNumber', '?')}")
            print(f"  End: offset {last.offset}, measure {getattr(last, 'measureNumber', '?')}")
