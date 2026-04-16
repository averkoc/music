"""Check what's in the trill spanner"""
from music21 import converter

score = converter.parse('musescore_files/violin_reference_test.xml')
part = score.parts[0]

# Find trill spanner
for spanner in part.flatten().spanners:
    if 'trill' in spanner.__class__.__name__.lower():
        print(f"{spanner.__class__.__name__} spanner:")
        print(f"  getFirst(): {spanner.getFirst()}")
        print(f"  getLast(): {spanner.getLast()}")
        print(f"\n  getAllElements() contains {len(list(spanner))} elements:")
        for i, el in enumerate(spanner):
            meas = getattr(el, 'measureNumber', '?')
            offset = getattr(el, 'offset', '?')
            print(f"    {i}: M{meas}, offset={offset}, {el}")
