"""Check note-off velocities in generated MIDI file."""
import mido
from collections import Counter

mid = mido.MidiFile('midi_output/testisakso2_violin_swam.mid')
note_offs = [msg for msg in mid.tracks[0] if msg.type == 'note_off']
velocities = [msg.velocity for msg in note_offs]

print('✓ Note-Off Velocity Analysis:')
print(f'  Total note-offs: {len(note_offs)}')
print(f'  Unique velocities: {len(set(velocities))}')

vel_counts = Counter(velocities)
print(f'  Velocity breakdown:')
for vel, count in sorted(vel_counts.items()):
    if vel <= 20:
        vel_type = 'Very smooth (gliss/slur)'
    elif vel <= 40:
        vel_type = 'Smooth (legato/tenuto)'
    elif vel <= 70:
        vel_type = 'Medium (normal)'
    elif vel <= 95:
        vel_type = 'Firm (accent)'
    elif vel <= 115:
        vel_type = 'Sharp (staccato)'
    else:
        vel_type = 'Very sharp (staccatissimo)'
    print(f'    Velocity {vel:3d}: {count:2d} notes - {vel_type}')
