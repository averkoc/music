"""Check slur and vibrato ranges after fix"""
from music21 import converter

score = converter.parse('musescore_files/violin_reference_test.xml')
part = score.parts[0]

print("="*60)
print("SLUR SPANNERS")
print("="*60)
for spanner in part.flatten().spanners:
    if spanner.__class__.__name__ == 'Slur':
        first = spanner.getFirst()
        last = spanner.getLast()
        start_abs = first.getOffsetInHierarchy(part)
        end_abs = last.getOffsetInHierarchy(part) + last.duration.quarterLength
        print(f"\nSlur from offset {start_abs} to {end_abs}")
        print(f"  First: M{getattr(first, 'measureNumber', '?')}, {first.pitch.nameWithOctave}")
        print(f"  Last: M{getattr(last, 'measureNumber', '?')}, {last.pitch.nameWithOctave}")

print("\n" + "="*60)
print("VIBRATO SPANNERS")
print("="*60)
for spanner in part.flatten().spanners:
    if 'trill' in spanner.__class__.__name__.lower():
        first = spanner.getFirst()
        last = spanner.getLast()
        start_abs = first.getOffsetInHierarchy(part)
        end_abs = last.getOffsetInHierarchy(part) + last.duration.quarterLength
        print(f"\nVibrato from offset {start_abs} to {end_abs}")
        print(f"  First: M{getattr(first, 'measureNumber', '?')}, {first.pitch.nameWithOctave}, duration={first.duration.quarterLength}q")
        print(f"  Last: M{getattr(last, 'measureNumber', '?')}, {last.pitch.nameWithOctave}, duration={last.duration.quarterLength}q")
        
        # Check which notes fall in this range
        print(f"\n  Notes in this range:")
        for el in part.flatten().notesAndRests:
            if hasattr(el, 'pitch'):
                if start_abs <= el.offset < end_abs:
                    print(f"    M{el.measureNumber}: {el.pitch.nameWithOctave}, offset={el.offset}, dur={el.duration.quarterLength}q")
