"""Visualize the difference between baseline and explicit vibrato."""
import mido

def analyze_vibrato(filename):
    """Analyze CC1 values in MIDI file."""
    mid = mido.MidiFile(filename)
    track = mid.tracks[0]
    
    cc1_values = []
    current_time = 0
    
    for msg in track:
        current_time += msg.time
        if msg.type == 'control_change' and msg.control == 1:
            cc1_values.append(msg.value)
    
    if not cc1_values:
        return None, None, None
    
    # Categorize values
    no_vibrato = [v for v in cc1_values if v == 0]
    baseline = [v for v in cc1_values if 0 < v <= 30]
    explicit = [v for v in cc1_values if v > 30]
    
    return no_vibrato, baseline, explicit

print("=" * 80)
print("VIBRATO LEVEL COMPARISON")
print("=" * 80)

# Test file without explicit vibrato marks (baseline only)
print("\n1. sakso2.mxl (NO explicit vibrato marks - baseline vibrato only)")
print("-" * 80)
no_vib, baseline, explicit = analyze_vibrato('midi_output/test_baseline_vibrato.mid')
if baseline is not None:
    print(f"   No vibrato (CC1=0):     {len(no_vib):3d} messages")
    print(f"   Baseline vibrato (1-30): {len(baseline):3d} messages  ← Default ~20-25% intensity")
    print(f"   Explicit vibrato (31+):  {len(explicit):3d} messages")
    if baseline:
        print(f"   Baseline range: {min(baseline)}-{max(baseline)}")

# Test file with explicit vibrato marks
print("\n2. testisakso2.mxl (4 explicit vibrato marks + baseline on other notes)")
print("-" * 80)
no_vib, baseline, explicit = analyze_vibrato('midi_output/test_both_vibratos.mid')
if baseline is not None:
    print(f"   No vibrato (CC1=0):     {len(no_vib):3d} messages")
    print(f"   Baseline vibrato (1-30): {len(baseline):3d} messages  ← Default for most notes")
    print(f"   Explicit vibrato (31+):  {len(explicit):3d} messages  ← Marked notes (stronger)")
    if baseline:
        print(f"   Baseline range: {min(baseline)}-{max(baseline)}")
    if explicit:
        print(f"   Explicit range: {min(explicit)}-{max(explicit)}")

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)
print("""
✓ Baseline vibrato (~20-25 CC1): Applied to all quarter notes and longer
  - Mimics natural violin tone production
  - Excluded from staccato/staccatissimo/spiccato
  - Subtle, continuous variation with jitter

✓ Explicit vibrato (~40-50 CC1): Applied to notes with vibrato marks
  - Stronger, more expressive vibrato
  - Overrides baseline for marked notes
  - Pitch-dependent depth and rate

This creates realistic performance where:
- Most sustained notes have natural baseline vibrato
- Marked passages have stronger, more pronounced vibrato
- Short articulated notes remain crisp without vibrato
""")
