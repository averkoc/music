"""Test determinism by processing the same file twice."""
import subprocess
import mido
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else 'musescore_files/violintest.xml'

print("=" * 80)
print("DETERMINISM TEST")
print("=" * 80)
print(f"\nProcessing {filename} twice and comparing output...")

# Process first time
print("\n1st run...")
subprocess.run([
    'python', 'scripts/process_musicxml.py',
    filename, '-i', 'violin',
    '-o', 'midi_output/test_run1.mid'
], capture_output=True)

# Process second time
print("2nd run...")
subprocess.run([
    'python', 'scripts/process_musicxml.py',
    filename, '-i', 'violin',
    '-o', 'midi_output/test_run2.mid'
], capture_output=True)

# Compare the two outputs
mid1 = mido.MidiFile('midi_output/test_run1.mid')
mid2 = mido.MidiFile('midi_output/test_run2.mid')

track1 = mid1.tracks[0]
track2 = mid2.tracks[0]

print(f"\nComparing MIDI files...")
print(f"  Run 1: {len(list(track1))} messages")
print(f"  Run 2: {len(list(track2))} messages")

differences = []
for i, (msg1, msg2) in enumerate(zip(track1, track2)):
    if msg1 != msg2:
        differences.append((i, msg1, msg2))

print("\n" + "=" * 80)
if len(differences) == 0:
    print("✓ DETERMINISTIC: Both runs produced identical MIDI files")
else:
    print(f"❌ NON-DETERMINISTIC: Found {len(differences)} differences")
    print("\nFirst 10 differences:")
    for i, (idx, msg1, msg2) in enumerate(differences[:10]):
        print(f"\n  Message {idx}:")
        print(f"    Run 1: {msg1}")
        print(f"    Run 2: {msg2}")
        
        # Identify what changed
        if msg1.type == msg2.type == 'control_change':
            if msg1.control == msg2.control:
                print(f"    → CC{msg1.control} value: {msg1.value} vs {msg2.value} (Δ={msg2.value-msg1.value})")

print("\n" + "=" * 80)
print("SOURCES OF RANDOMNESS:")
print("=" * 80)
print("""
ALWAYS ACTIVE (causes non-determinism):
  - Bow force (CC20): ±3 to ±5 random variation
  - Bow position (CC21): ±2 to ±3 random variation
  Applied to: staccato, accent, marcato, and plain notes

OPTIONAL (disabled by default):
  - Humanization: timing, velocity, expression jitter
  
To make processing deterministic, you would need to:
  1. Set a random seed at the start of process_musicxml.py
  2. OR remove the random.randint() calls from bow force/position
""")
print("=" * 80)
