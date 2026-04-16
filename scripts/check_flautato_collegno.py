"""
Check if technique CC messages are working correctly in MIDI output.
Tracks CC20 (bow force), CC21 (bow position), and CC61 (bow mode).
"""
import mido
import sys

def analyze_cc_messages(midi_file):
    """Analyze technique-related CC messages in MIDI file."""
    mid = mido.MidiFile(midi_file)
    
    cc20_messages = []  # Bow Force
    cc21_messages = []  # Bow Position
    cc61_messages = []  # Bow Mode
    
    for i, track in enumerate(mid.tracks):
        print(f"\n=== Track {i}: {track.name} ===")
        track_time = 0
        
        for msg in track:
            track_time += msg.time
            
            if msg.type == 'control_change':
                if msg.control == 20:
                    cc20_messages.append({
                        'time': track_time,
                        'value': msg.value,
                        'track': i
                    })
                    technique = ""
                    if msg.value == 15:
                        technique = " [FLAUTATO]"
                    elif msg.value == 125:
                        technique = " [SCRATCH]"
                    elif msg.value == 64:
                        technique = " [RESET]"
                    print(f"  CC20 (Bow Force) = {msg.value} @ time {track_time}{technique}")
                    
                elif msg.control == 21:
                    cc21_messages.append({
                        'time': track_time,
                        'value': msg.value,
                        'track': i
                    })
                    technique = ""
                    if msg.value == 15:
                        technique = " [SUL TASTO]"
                    elif msg.value == 115:
                        technique = " [SUL PONTICELLO]"
                    elif msg.value == 64:
                        technique = " [RESET]"
                    print(f"  CC21 (Bow Position) = {msg.value} @ time {track_time}{technique}")
                    
                elif msg.control == 61:
                    cc61_messages.append({
                        'time': track_time,
                        'value': msg.value,
                        'track': i
                    })
                    mode = ""
                    if msg.value == 5:
                        mode = " [ARCO]"
                    elif msg.value == 50:
                        mode = " [PIZZICATO]"
                    elif msg.value == 90:
                        mode = " [COL LEGNO]"
                    print(f"  CC61 (Bow Mode) = {msg.value} @ time {track_time}{mode}")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"{'='*60}")
    print(f"Total CC20 (Bow Force) messages: {len(cc20_messages)}")
    print(f"Total CC21 (Bow Position) messages: {len(cc21_messages)}")
    print(f"Total CC61 (Bow Mode) messages: {len(cc61_messages)}")
    
    if cc20_messages:
        print(f"\nCC20 values found: {sorted(set(msg['value'] for msg in cc20_messages))}")
        if 15 in [msg['value'] for msg in cc20_messages]:
            print("  ✅ Found CC20=15 (FLAUTATO)")
        else:
            print("  ❌ Missing CC20=15 (FLAUTATO)")
            
        if 125 in [msg['value'] for msg in cc20_messages]:
            print("  ✅ Found CC20=125 (SCRATCH)")
        else:
            print("  ❌ Missing CC20=125 (SCRATCH)")
            
        if 64 in [msg['value'] for msg in cc20_messages]:
            print("  ✅ CC20 resets to default (64)")
    else:
        print("  ❌ NO CC20 messages found at all!")
    
    if cc21_messages:
        print(f"\nCC21 values found: {sorted(set(msg['value'] for msg in cc21_messages))}")
        if 15 in [msg['value'] for msg in cc21_messages]:
            print("  ✅ Found CC21=15 (SUL TASTO)")
        if 115 in [msg['value'] for msg in cc21_messages]:
            print("  ✅ Found CC21=115 (SUL PONTICELLO)")
        if 64 in [msg['value'] for msg in cc21_messages]:
            print("  ✅ CC21 resets to default (64)")
    
    if cc61_messages:
        print(f"\nCC61 values found: {sorted(set(msg['value'] for msg in cc61_messages))}")
        if 90 in [msg['value'] for msg in cc61_messages]:
            print("  ✅ Found CC61=90 (COL LEGNO)")
        else:
            print("  ❌ Missing CC61=90 (COL LEGNO)")
            
        if 50 in [msg['value'] for msg in cc61_messages]:
            print("  ✅ Found CC61=50 (PIZZICATO)")
        else:
            print("  ❌ Missing CC61=50 (PIZZICATO)")
    else:
        print("  ❌ NO CC61 messages found at all!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        midi_file = sys.argv[1]
    else:
        # Default to test file
        midi_file = "midi_output/test_complete_violin_swam.mid"
    
    print(f"Analyzing: {midi_file}")
    analyze_cc_messages(midi_file)
