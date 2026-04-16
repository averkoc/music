"""
Diagnose vibrato and legato issues in violin_reference_test
"""
import mido

mid = mido.MidiFile('midi_output/violin_reference_test_violin_swam.mid')
track = mid.tracks[0]

abs_time = 0
note_times = {}  # note number -> (on_time, off_time, velocity)
cc1_events = []  # (time, value) for modulation/vibrato
cc64_events = []  # (time, value) for sustain/legato

# Collect events
for msg in track:
    abs_time += msg.time
    
    if msg.type == 'note_on' and msg.velocity > 0:
        note_times[msg.note] = [abs_time, None, msg.velocity]
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in note_times:
            note_times[msg.note][1] = abs_time
    elif msg.type == 'control_change':
        if msg.control == 1:  # Modulation/Vibrato
            cc1_events.append((abs_time, msg.value))
        elif msg.control == 64:  # Sustain/Legato
            cc64_events.append((abs_time, msg.value))

print("=" * 60)
print("VIBRATO ANALYSIS (CC1)")
print("=" * 60)
print(f"\nTotal CC1 events: {len(cc1_events)}")
print("\nMeasure 8 should have vibrato (A5 = note 81, whole note)")
if 81 in note_times:
    on_time, off_time, vel = note_times[81]
    print(f"  Note 81 (A5): ON at {on_time}, OFF at {off_time}, duration={off_time-on_time}")
    
    # Find CC1 events near this note
    cc1_during_note = [(t, v) for t, v in cc1_events if on_time <= t <= off_time]
    cc1_before_note = [(t, v) for t, v in cc1_events if on_time - 500 <= t < on_time]
    
    print(f"\n  CC1 events DURING note 81:")
    if cc1_during_note:
        for t, v in cc1_during_note:
            print(f"    Time {t} (offset +{t-on_time}): CC1={v}")
    else:
        print(f"    ❌ NO CC1 events during the note!")
    
    print(f"\n  CC1 events BEFORE note 81:")
    for t, v in cc1_before_note[-5:]:
        print(f"    Time {t} (offset {t-on_time}): CC1={v}")

print("\n" + "=" * 60)
print("LEGATO ANALYSIS (CC64)")
print("=" * 60)
print(f"\nTotal CC64 events: {len(cc64_events)}")
print("CC64 should be ON (127) only for slurred passages")
print("\nAll CC64 changes:")
for t, v in cc64_events:
    state = "ON (LEGATO)" if v == 127 else "OFF"
    print(f"  Time {t}: CC64={v} -> {state}")

# Find which notes play during CC64=127
if len(cc64_events) >= 2:
    # Find when CC64 goes ON and OFF
    legato_ranges = []
    for i in range(len(cc64_events)-1):
        if cc64_events[i][1] == 127:
            start = cc64_events[i][0]
            end = cc64_events[i+1][0]
            legato_ranges.append((start, end))
    
    print(f"\nNotes playing during CC64=ON (legato mode):")
    for note_num, (on_t, off_t, vel) in note_times.items():
        for leg_start, leg_end in legato_ranges:
            if on_t >= leg_start and on_t < leg_end:
                note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note_num % 12]
                octave = note_num // 12 - 1
                print(f"  Note {note_num} ({note_name}{octave}): ON at {on_t}")

print("\n" + "=" * 60)
print("ARTICULATION SUMMARY")
print("=" * 60)
print(f"Total notes: {len(note_times)}")
print(f"Notes with vibrato CC1 active: {len([n for n, (on, off, v) in note_times.items() if any(on <= t <= off for t, val in cc1_events if val > 20)])}")
print(f"Notes with legato CC64 active: {len([n for n, (on, off, v) in note_times.items() if any(on <= t <= off for t, val in cc64_events if val == 127)])}")
