"""Check which notes have vibrato marks and their durations."""
import mido
from music21 import converter
from articulation_detector import MusicXMLArticulationDetector, ArticulationType

# Load score
score = converter.parse('musescore_files/testisakso2.mxl')
detector = MusicXMLArticulationDetector()
note_articulations, dynamics = detector.analyze_score(score)

print("Notes with vibrato:")
print("-" * 80)
for note in note_articulations:
    if ArticulationType.VIBRATO in note.articulations:
        pitch_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note.pitch % 12]
        octave = note.pitch // 12 - 1
        duration_sec = note.duration * 0.5  # Assuming 120 BPM
        print(f"Note {note.note_index}: {pitch_name}{octave} (MIDI {note.pitch})")
        print(f"  Duration: {note.duration:.2f} quarter notes ({duration_sec:.2f} seconds)")
        print(f"  Onset: {note.onset_time:.2f}")
        print()

# Also check MIDI CC messages
print("\n" + "=" * 80)
print("MIDI CC Messages in generated file:")
print("="  * 80)

mid = mido.MidiFile('midi_output/test_vibrato_enhanced.mid')
track = mid.tracks[0]

current_time = 0
note_on_time = {}

for msg in track:
    current_time += msg.time
    
    if msg.type == 'note_on' and msg.velocity > 0:
        pitch_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][msg.note % 12]
        octave = msg.note // 12 - 1
        note_on_time[msg.note] = current_time
        print(f"\n-- Note ON: {pitch_name}{octave} (MIDI {msg.note}) at tick {current_time}")
    
    elif msg.type == 'control_change' and msg.control in [1, 17]:
        cc_name = "CC1 (Vibrato Depth)" if msg.control == 1 else "CC17 (Vibrato Rate)"
        print(f"   {cc_name}: value={msg.value} (offset +{msg.time} ticks)")
        
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in note_on_time:
            duration = current_time - note_on_time[msg.note]
            print(f"   Note OFF at tick {current_time} (duration: {duration} ticks)")
