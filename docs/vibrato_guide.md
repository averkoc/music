# Vibrato Detection in MuseScore

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

When vibrato is detected, the converter:

1. **Delays onset** (500ms default)
   - Real performers don't add vibrato immediately
   - Note starts clean, vibrato develops naturally

2. **Gradual ramp** (300ms default)
   - CC1 (Modulation) gradually increases from 0 to target depth
   - Avoids sudden "wobble" effect

3. **Target depth** (CC1 = 64 default)
   - 0 = no vibrato
   - 64 = moderate vibrato (natural)
   - 127 = intense vibrato

## Configuration

Vibrato settings in `config/swam_config.json`:

```json
"vibrato_mark": {
  "cc1_target": 64,
  "delay_ms": 500,
  "ramp_duration_ms": 300,
  "description": "Gradually add vibrato after note onset"
}
```

## Example: Applying Vibrato in MuseScore

### For a sustained note:
```
MuseScore notation:
[Whole note C] ~~~~~ (wavy line)

MIDI output:
t=0: Note ON C
t=500ms: CC1 starts ramping from 0 → 64
t=800ms: CC1 reaches 64 (vibrato fully developed)
t=1920: Note OFF
```

### For a phrase:
```
MuseScore notation:
[C] [D] [E] [F]
~~~~~~~~~~~~~~~~~~~~~ (wavy line over all)

MIDI output:
All four notes get vibrato treatment with delayed onset
```

## SWAM CC1 (Modulation/Vibrato)

| CC1 Value | Effect |
|-----------|--------|
| 0 | No vibrato (straight tone) |
| 20-40 | Light vibrato (subtle) |
| 50-70 | Moderate vibrato (natural) |
| 80-100 | Strong vibrato (expressive) |
| 110-127 | Very intense vibrato (dramatic) |

## Testing Vibrato

Create a test MuseScore file with vibrato:
```bash
# Process with verbose to see vibrato detection
python scripts/process_musicxml.py vibrato_test.mxl --instrument violin --verbose
```

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
