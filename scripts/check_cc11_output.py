"""Check if CC11 values reflect the dynamic changes in the MIDI output."""
import mido

mid = mido.MidiFile('midi_output/violintest_violin_swam.mid')
track = mid.tracks[0]

print("=" * 80)
print("CC11 (EXPRESSION) VALUES IN GENERATED MIDI")
print("=" * 80)

# Track CC11 values before each note
cumulative_time = 0
note_count = 0
last_cc11 = None

print(f"\n{'Note#':<8} {'Time':<10} {'Pitch':<8} {'Vel':<6} {'CC11':<8} {'Expected':<12}")
print("-" * 80)

for msg in track:
    cumulative_time += msg.time
    
    if msg.type == 'control_change' and msg.control == 11:
        last_cc11 = msg.value
    
    elif msg.type == 'note_on' and msg.velocity > 0:
        note_count += 1
        
        # Determine expected dynamic based on our analysis
        if note_count <= 16:
            expected = "mf (80)"
        elif note_count <= 36:
            expected = "f (95)"
        else:
            expected = "mf (80)"
        
        pitch_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][msg.note % 12]
        octave = msg.note // 12 - 1
        
        # Check if CC11 matches expectation
        marker = ""
        if note_count == 1:
            marker = " ← First note"
        elif note_count == 17:
            marker = " ← Should be f (95)"
        elif note_count == 37:
            marker = " ← Should return to mf (80)"
        
        # Check for issues
        if last_cc11 is None:
            issue = " ⚠ NO CC11 SENT!"
        elif (note_count <= 16 and abs(last_cc11 - 80) > 15):
            issue = f" ⚠ Wrong! Should be ~80"
        elif (17 <= note_count <= 36 and abs(last_cc11 - 95) > 15):
            issue = f" ⚠ Wrong! Should be ~95"
        elif (note_count >= 37 and abs(last_cc11 - 80) > 15):
            issue = f" ⚠ Wrong! Should be ~80"
        else:
            issue = ""
        
        print(f"{note_count:<8} {cumulative_time:<10} {pitch_name}{octave:<6} {msg.velocity:<6} {last_cc11 if last_cc11 is not None else 'None':<8} {expected:<12}{marker}{issue}")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)

# Count distinct CC11 values
cc11_values = []
curr_time = 0
for msg in track:
    curr_time += msg.time
    if msg.type == 'control_change' and msg.control == 11:
        cc11_values.append(msg.value)

unique_cc11 = set(cc11_values)
print(f"\nUnique CC11 values sent: {sorted(unique_cc11)}")
print(f"Total CC11 messages: {len(cc11_values)}")

if len(unique_cc11) < 2:
    print("\n❌ PROBLEM: Only one CC11 value used!")
    print("   Dynamics are being detected but not applied as different CC11 values")
else:
    print("\n✓ Multiple CC11 values found")
    print("  Dynamics are being converted to MIDI CC11 messages")

print("=" * 80)
