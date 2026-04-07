"""
Analyze glissando MIDI events in detail.
"""
import sys
import mido

def analyze_glissando(midi_path):
    mid = mido.MidiFile(midi_path)
    track = mid.tracks[0]
    
    time = 0
    gliss_region_start = 22000
    gliss_region_end = 24000
    
    print(f"Analyzing glissando region (time {gliss_region_start} - {gliss_region_end}):\n")
    
    for msg in track:
        time += msg.time
        
        if gliss_region_start <= time <= gliss_region_end:
            if msg.type == 'control_change' and msg.control in [5, 64]:
                cc_name = {5: 'Portamento', 64: 'Sustain/Legato'}[msg.control]
                print(f"Time {time:6d}: CC{msg.control:2d} ({cc_name:15s}) = {msg.value:3d}")
            elif msg.type in ['note_on', 'note_off']:
                if msg.type == 'note_on' and msg.velocity > 0:
                    print(f"Time {time:6d}: Note ON  {msg.note:3d} (vel={msg.velocity})")
                else:
                    print(f"Time {time:6d}: Note OFF {msg.note:3d}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_glissando_events.py <midi_file>")
        sys.exit(1)
    
    analyze_glissando(sys.argv[1])
