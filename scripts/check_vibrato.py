from music21 import converter

score = converter.parse('musescore_files/testisakso2.mxl')
part = score.parts[0]
notes = list(part.flatten().notes)

print('Generic articulations with style:')
for n in notes[:30]:
    for a in n.articulations:
        if type(a).__name__ == 'Articulation':
            print(f'Note {n.pitch.nameWithOctave}: name="{a.name}"')
            if hasattr(a, 'style') and a.style:
                print(f'  style: {a.style}')
                if hasattr(a.style, '__dict__'):
                    print(f'  style.__dict__: {a.style.__dict__}')
