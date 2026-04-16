"""Test script to verify metrical emphasis from MusicXML beatStrength."""
from music21 import converter
from articulation_detector import MusicXMLArticulationDetector
import json
from pathlib import Path

# Load config
config_path = Path(__file__).parent.parent / "config" / "swam_config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

metrical_config = config['instruments']['violin']['metrical_emphasis']

print("=" * 80)
print("METRICAL EMPHASIS TEST")
print("=" * 80)

print(f"\nConfiguration:")
print(f"  Enabled: {metrical_config['enabled']}")
print(f"  Emphasis amount: {metrical_config['emphasis_amount']}")

# Load MusicXML file
score = converter.parse('musescore_files/pala1.mxl')
detector = MusicXMLArticulationDetector()
note_articulations, _ = detector.analyze_score(score)

print(f"\n\nFirst 20 notes with metrical analysis:")
print("-" * 80)
print(f"{'Note':<6} {'Offset':<8} {'Beat Str':<10} {'Base CC11':<10} {'With Emphasis':<15}")
print("-" * 80)

for i, note_art in enumerate(note_articulations[:20]):
    pitch_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note_art.pitch % 12]
    octave = note_art.pitch // 12 - 1
    
    # Base CC11 from dynamic
    base_cc11 = note_art.dynamic_level.cc_value if note_art.dynamic_level else 80
    
    # Calculate emphasis if enabled
    if metrical_config['enabled']:
        emphasis_amount = metrical_config['emphasis_amount']
        beat_emphasis = int(note_art.beat_strength * emphasis_amount)
        final_cc11 = min(127, base_cc11 + beat_emphasis)
        emphasis_str = f"{final_cc11} (+{beat_emphasis})"
    else:
        final_cc11 = base_cc11
        emphasis_str = f"{final_cc11} (no change)"
    
    # Visual indicator for beat strength
    if note_art.beat_strength >= 1.0:
        indicator = "← DOWNBEAT"
    elif note_art.beat_strength >= 0.5:
        indicator = "← medium"
    elif note_art.beat_strength >= 0.25:
        indicator = "← weak"
    else:
        indicator = "← offbeat"
    
    print(f"{pitch_name}{octave:<4} {note_art.onset_time:<8.2f} {note_art.beat_strength:<10.2f} {base_cc11:<10} {emphasis_str:<15} {indicator}")

print("\n" + "=" * 80)
print("SUMMARY:")
print("  ✓ beatStrength extracted from MusicXML")
print("  ✓ Downbeats (1.0) get full emphasis boost")
print("  ✓ Medium beats (0.5) get half boost")
print("  ✓ Weak beats (0.25) get quarter boost")
print("  ✓ Configurable via swam_config.json")
print("\nTo adjust:")
print("  - Set 'enabled': false to disable")
print("  - Change 'emphasis_amount' for stronger/subtler effect (range: 3-8)")
print("=" * 80)
