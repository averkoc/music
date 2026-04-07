# Advanced Vibrato System for SWAM Instruments

This guide covers the sophisticated vibrato implementation designed for realistic SWAM violin and saxophone performance.

## Overview

The vibrato system implements recommendations from professional SWAM users and AI analysis to create vibrato that sounds like a living, breathing performer rather than a synthesizer. It uses:

- **CC1 (Modulation)**: Vibrato depth
- **CC17**: Vibrato rate/speed  
- **Pitch-dependent parameters**: Different vibrato for low, mid, and high notes
- **Continuous jitter**: Human-like variation that breaks synthetic patterns
- **Natural onset**: Delayed ramp (notes start clean, vibrato develops gradually)

## The Problem with Static Vibrato

Setting CC1 to a constant value (e.g., CC1=64 throughout) creates an unnatural, synthetic sound because:
- Real performers don't start vibrato instantly
- Vibrato depth and rate naturally fluctuate
- The human brain recognizes perfectly steady patterns as "fake"
- Vibrato characteristics vary by pitch range

## How to Add Vibrato in MuseScore

Vibrato can be notated in MuseScore in several ways, and the converter now detects all of them:

### Method 1: Wavy Line (Recommended)
1. Select the note where vibrato should start
2. From the palette, go to **Lines** → **Wavy Line** (or Trill line)
3. Drag and extend the wavy line to cover the desired notes
4. The converter will detect all notes under the wavy line as vibrato

**Detection**: Automatically finds wavy line/trill spanners

### Method 2: Staff Text Expression
1. Select a note
2. Add **Staff Text** (Ctrl+T / Cmd+T)
3. Type "vibrato", "vib.", or "vib"
4. The note will be marked with vibrato articulation

**Detection**: Searches expression text for vibrato keywords

### Method 3: Articulation Mark
Some MuseScore versions support vibrato as an articulation:
1. Select note
2. Add vibrato articulation from palette (if available)

**Detection**: Checks articulation class names for "vibrato" or "tremolo"

### Technical Note: MuseScore SMuFL Vibrato Symbols

MuseScore exports vibrato articulation marks using SMuFL (Standard Music Font Layout) symbols like `wiggleVibratoLargeSlowest` in MusicXML's `<other-articulation>` element. The music21 library parses these as generic `Articulation` objects without preserving the SMuFL symbol name.

**Workaround**: The converter detects all generic `Articulation` objects (those without specific subclass types) as vibrato. This works correctly for typical MuseScore files where custom articulations are primarily vibrato marks.

If you use other custom articulations that shouldn't be vibrato, prefer the wavy line method instead.

## How the Converter Handles Vibrato

When vibrato is detected on a note, the converter creates a sophisticated multi-stage vibrato:

### Stage 1: Duration Check
- **Minimum duration**: 0.5 seconds (configurable)
- Short notes (staccato, eighth notes) are **skipped** - a real performer can't vibrato a quick note
- Only sustained notes get vibrato treatment

### Stage 2: Pitch Analysis
The system automatically adjusts vibrato based on the note's pitch:

| Pitch Range | CC1 (Depth) | CC17 (Rate) | Effect |
|-------------|-------------|-------------|--------|
| **Low** (< D4) | 50 | 60 | Wider, slower vibrato (G/D strings) |
| **Mid** (D4-D5) | 45 | 67 | Balanced vibrato |
| **High** (> D5) | 40 | 75 | Narrower, faster vibrato (A/E strings) |

This mimics how real violinists naturally use different vibrato on different strings.

### Stage 3: Natural Onset (Delay + Ramp)
The vibrato doesn't start instantly:

1. **Delay (200ms default)**: Note starts with clean, straight tone
2. **Ramp (150ms default)**: CC1 gradually increases from 0 to target depth over 8 steps
3. **CC17 set immediately**: Vibrato rate is established at note start

Example timing for a 1-second note:
```
t=0ms:    Note ON, CC1=0, CC17=67 (ready but not active)
t=200ms:  CC1 starts ramping (5, 11, 16, 22, 28, 33, 39, 45)
t=350ms:  CC1 reaches target (45), vibrato fully developed
t=350-1000ms: Jitter phase (see below)
```

### Stage 4: Continuous Jitter (The Secret Sauce)
After the vibrato reaches target depth, it doesn't stay constant. Instead, it **fluctuates naturally** throughout the note sustain:

- **CC1 jitter**: ±5 from target every 50ms
  - Target 45 → varies between 40-50
- **CC17 jitter**: ±3 from target (less frequent)
  - Target 67 → varies between 64-70

This creates 10-20 unique CC messages per note instead of 1-2, breaking the synthetic pattern the brain recognizes as "machine-like."

### Example: Full Vibrato Profile for D4 (1 second)
```
Time    CC1   CC17  Description
0ms     0     67    Note starts, rate set
200ms   5     67    Vibrato begins to develop
218ms   11    67    Ramp step 2
236ms   16    67    Ramp step 3
254ms   22    67    Ramp step 4
272ms   28    67    Ramp step 5
290ms   33    67    Ramp step 6
308ms   39    67    Ramp step 7
326ms   45    67    Target reached
374ms   48    69    Jitter +3 depth, +2 rate
422ms   42    67    Jitter -3 depth, 0 rate
470ms   47    65    Jitter +2 depth, -2 rate
518ms   43    68    Jitter -2 depth, +1 rate
```

## Sweet Spot Values

Based on professional recommendations:

| Parameter | Recommended Range | Notes |
|-----------|------------------|-------|
| **CC1 (Depth)** | 30-55 | Classical natural range. 80+ sounds "nervous" |
| **CC17 (Rate)** | 60-75 | Natural hand speed. <40 = sickly, >90 = jittery |

Current defaults:
- Low notes: CC1=50, CC17=60
- Mid notes: CC1=45, CC17=67  
- High notes: CC1=40, CC17=75

## Configuration

All vibrato settings in [config/swam_config.json](../config/swam_config.json) under `vibrato_mark`:

```json
"vibrato_mark": {
  "cc1_target": 45,
  "cc17_target": 67,
  "delay_ms": 200,
  "ramp_duration_ms": 150,
  "pitch_dependent": {
    "enabled": true,
    "low_notes": {
      "threshold": "D4",
      "cc1_depth": 50,
      "cc17_rate": 60
    },
    "high_notes": {
      "threshold": "D5",
      "cc1_depth": 40,
      "cc17_rate": 75
    }
  },
  "jitter": {
    "enabled": true,
    "cc1_range": 5,
    "cc17_range": 3,
    "interval_ms": 50
  },
  "min_duration_seconds": 0.5
}
```

### Customization Tips

**For more intense vibrato:**
- Increase `cc1_target` to 55-60
- Increase `cc1_range` to 7-8 for more variation

**For subtle vibrato:**
- Decrease `cc1_target` to 35-40
- Decrease `cc1_range` to 3-4

**For faster onset:**
- Decrease `delay_ms` to 100-150
- Decrease `ramp_duration_ms` to 100

**To disable jitter** (precise vibrato):
```json
"jitter": {
  "enabled": false
}
```

**To disable pitch-dependent vibrato** (uniform across all notes):
```json
"pitch_dependent": {
  "enabled": false
}
```

## Example: Applying Vibrato in MuseScore

### For a sustained note:
```
MuseScore notation:
[Whole note C] ~~~~~ (wavy line)

MIDI output:
t=0ms:    Note ON C, CC1=0, CC17=67
t=200ms:  CC1 ramps 0 → 45 (8 steps over 150ms)
t=350ms:  Jitter begins (CC1: 40-50, CC17: 64-70)
t=3840ms: Note OFF
```

### For a phrase:
```
MuseScore notation: [C] [D] [E] [F]
                    ~~~~~~~~~~~~~~~~~~~~~ (wavy line over all)

MIDI output:
Each note gets full vibrato treatment:
- Natural onset delay (200ms)
- Gradual ramp (150ms)  
- Continuous jitter during sustain
- Pitch-dependent depth/rate
```

## SWAM CC Reference

| CC Number | Parameter | Natural Range | Effect |
|-----------|-----------|---------------|--------|
| **CC1** | Modulation/Vibrato Depth | 30-55 | Amount of pitch variation |
| **CC17** | Vibrato Rate | 60-75 | Speed of vibrato cycles (Hz) |

### CC1 (Vibrato Depth) Guide
| Value | Effect | Use Case |
|-------|--------|----------|
| 0 | No vibrato (straight tone) | Staccato, fast passages |
| 20-40 | Light vibrato (subtle) | Baroque style, chamber music |
| 40-55 | Moderate vibrato (natural) | **Classical default** |
| 60-80 | Strong vibrato (expressive) | Romantic solos, climaxes |
| 80+ | Intense vibrato (dramatic) | High emotion, but use sparingly |

### CC17 (Vibrato Rate) Guide
| Value | Speed (approx Hz) | Effect | Use Case |
|-------|------------------|--------|----------|
| < 40 | Very slow (~4 Hz) | Sickly, unnatural | ❌ Avoid |
| 50-60 | Slow (~5 Hz) | Relaxed, wide | Low strings, emotional |
| 60-70 | Moderate (~6 Hz) | **Natural classical range** | Default |
| 70-85 | Fast (~7 Hz) | Bright, energetic | High strings, excitement |
| 90+ | Very fast (~8+ Hz) | Jittery, electric | ❌ Avoid unless intentional |

## Testing Vibrato

Create a test MuseScore file with vibrato marks on notes of different pitches and durations:

```bash
# Process with verbose to see vibrato detection
python scripts/process_musicxml.py test_vibrato.mxl -i violin -o output.mid -v

# Expected output:
# Articulations detected:
#   - vibrato: 4
# 
# Notes < 0.5 seconds will be skipped
# Notes will have pitch-dependent CC1/CC17 values
```

### Inspect Generated MIDI

```bash
python scripts/inspect_midi_ccs.py output.mid
```

Look for:
- **CC1**: Should show 15-25 unique values (indicating jitter)
- **CC17**: Should show 5-10 unique values
- **Range**: CC1 around 35-55, CC17 around 60-75

## Advanced: Understanding the Algorithm

The vibrato system uses discrete MIDI CC messages injected at specific time offsets. This is **not** using automation lanes or continuous curves - it's individual MIDI messages.

### Message Injection Strategy

**At note-on** (before the Note ON event):
1. Set CC1=0 (no vibrato yet)
2. Set CC17 to target rate (rate ready but depth is 0)
3. Wait delay_ms
4. Ramp CC1 in 8 steps to target depth

**During note sustain** (after Note ON event):
1. Every 50ms, send new CC1 with jitter (±5 from target)
2. Every 100ms, send new CC17 with jitter (±3 from target)
3. Random variation breaks pattern recognition

**At note-off**:
- CC1 is NOT reset to 0 (vibrato can carry to next note if marked)
- For notes without vibrato mark, CC1 is explicitly set to 0

### Why Jitter Matters

Human brains are pattern-recognition machines. A perfectly steady CC1=45 throughout a note **sounds synthetic** because:
- No human can maintain exact 6.00000 Hz oscillation
- Natural vibrato has micro-variations in depth and rate
- The auditory cortex recognizes perfect repetition as "not human"

Adding ±5 variation (10% of the range) is enough to break this pattern while staying musically natural.

## Troubleshooting

**Vibrato sounds too intense:**
- Lower `cc1_target` in config (try 35-40 instead of 45)
- Reduce `cc1_range` for jitter (try 3 instead of 5)

**Vibrato starts too late:**
- Reduce `delay_ms` (try 100-150 instead of 200)
- Reduce `ramp_duration_ms` (try 100 instead of 150)

**Vibrato stays constant (no variation):**
- Check `jitter.enabled` is `true` in config
- Ensure note duration > 0.5 seconds (shorter notes skip vibrato)
- Check MIDI output has 15+ unique CC1 values (not just 2-3)

**Wrong vibrato for pitch range:**
- Check `pitch_dependent.enabled` is `true`
- Verify thresholds in config (D4=MIDI 62, D5=MIDI 74)
- High notes should show CC17=75, low notes CC17=60

**No vibrato at all:**
- Ensure notes have vibrato **articulation marks or wavy lines** in MuseScore
- Notes < 0.5 seconds are intentionally skipped
- Check verbose output: should show "vibrato: N" in detected articulations

## Credits & References

This implementation is based on:
- **Gemini AI analysis** of SWAM physical modeling requirements
- **Professional SWAM user recommendations** for CC value ranges
- **Neuroscience of pattern recognition** (why jitter matters)
- **Music21 library** for MusicXML parsing (with workarounds for SMuFL limitations)

For more details on SWAM CC mappings, see the official Audio Modeling Camelot preset reference.

You should see in the output:
```
Articulations detected:
  - vibrato: 4  ← Number of notes with vibrato
```

## Combining Vibrato with Humanization

When using humanization, the vibrato depth is slightly varied:
```bash
python scripts/process_musicxml.py input.mxl \
  --instrument violin \
  --humanize default
```

This adds natural variation to the CC1 target (±4 in default mode), making the vibrato feel more human.

## Troubleshooting

**No vibrato detected?**
- Check that you used one of the three methods above
- Verify the wavy line actually spans the notes
- Try adding "vibrato" as staff text to confirm detection works

**Vibrato too intense?**
- Lower `cc1_target` in config (try 50 instead of 64)

**Vibrato starts too soon?**
- Increase `delay_ms` in config (try 700ms)

**Vibrato transition too abrupt?**
- Increase `ramp_duration_ms` (try 500ms)
