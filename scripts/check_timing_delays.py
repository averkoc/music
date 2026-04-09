"""Check for timing delays in MIDI file."""
import mido

mid = mido.MidiFile('midi_output/testisakso2_violin_swam.mid')
track = mid.tracks[0]

note_ons = []
cumulative_time = 0

for msg in track:
    cumulative_time += msg.time
    if msg.type == 'note_on' and msg.velocity > 0:
        note_ons.append((msg.note, cumulative_time))

print("First 10 note onset times (in ticks):")
for i, (note, time) in enumerate(note_ons[:10]):
    if i > 0:
        interval = time - note_ons[i-1][1]
        print(f"Note {i+1}: tick {time:5d} (interval: {interval:4d} ticks)")
    else:
        print(f"Note {i+1}: tick {time:5d}")

print(f"\nTotal notes: {len(note_ons)}")
print(f"Ticks per beat: {mid.ticks_per_beat}")
