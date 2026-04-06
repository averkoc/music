# MusicXML Workflow Guide

Complete guide for using the **recommended MusicXML approach** to convert MuseScore compositions into expressive SWAM performances.

## Why MusicXML Over MIDI?

### What MIDI Export Loses:
- ❌ Articulation markings (converted to approximate note durations)
- ❌ Dynamic semantics (converted to velocity values)
- ❌ Slur and legato markings (no way to detect)
- ❌ Expression text ("dolce", "espressivo", etc.)
- ❌ Crescendo/diminuendo intentions (only velocity changes)

### What MusicXML Preserves:
- ✅ **Exact articulation types** (staccato vs. staccatissimo vs. accent)
- ✅ **Dynamic markings** (pp, mf, ff as semantic data, not just velocity)
- ✅ **Slur beginnings and endings** (explicit CC64 legato control)
- ✅ **Expression text** (can influence CC mapping)
- ✅ **Crescendo/diminuendo wedges** (smooth CC11 transitions)
- ✅ **All metadata** (tempo, key, time signature)

## Complete Workflow

### Step 1: Compose in MuseScore

**Best Practices for SWAM-Ready Scores:**

1. **Use articulations generously:**
   - Staccato (`.`) for short, detached notes
   - Accent (`>`) for emphasis
   - Marcato (`^`) for strong accents
   - Tenuto (`-`) for full-value notes
   - Slurs for legato phrases

2. **Add dynamic markings:**
   - Use standard dynamics (pp, p, mp, mf, f, ff, fff)
   - Add crescendo (`<`) and diminuendo (`>`) hairpins
   - Place dynamics at phrase beginnings

3. **Mark phrases clearly:**
   - Use slurs to indicate legato passages
   - Separate staccato sections from legato
   - Add phrase markings for musicality

4. **Expression text (optional):**
   - "dolce" for sweet, gentle passages
   - "espressivo" for expressive playing
   - "vibrato" or "non vibrato" to control CC1

### Step 2: Export  MusicXML

**In MuseScore:**

1. File → Export → MusicXML
2. Choose format:
   - **Compressed (.mxl)** - Smaller file, recommended
   - **Uncompressed (.musicxml)** - Easier to debug if needed
3. Save to `musescore_files/` folder
4. Use descriptive naming: `violin_sonata_movement1.musicxml`

**No special export settings needed** - MusicXML captures everything!

### Step 3: Process with Python Script

**Basic command:**
```bash
python scripts/process_musicxml.py musescore_files/your_file.musicxml --instrument violin
```

**With verbose output** (recommended first time):
```bash
python scripts/process_musicxml.py musescore_files/your_file.musicxml --instrument violin -v
```

**Verbose output shows:**
```
Loading MusicXML file: musescore_files/melody.musicxml
Analyzing articulations and dynamics...
  Found 127 notes
  Found 3 dynamic changes
  Articulations detected:
    - staccato: 45
    - accent: 12
    - legato: 35
Generating MIDI with SWAM CC messages...
Saving MIDI file: midi_output/melody_violin_swam.mid
✓ Processing complete!
```

**Custom output location:**
```bash
python scripts/process_musicxml.py musescore_files/piece.musicxml -i saxophone -o custom/output.mid
```

### Step 4: What the Script Does

The MusicXML processor performs sophisticated analysis:

#### Articulation Mapping

| MuseScore Articulation | SWAM CC Effect |
|------------------------|----------------|
| Staccato (.) | CC11 -20, duration 50%, CC74 +15 |
| Staccatissimo (.') | CC11 -30, duration 25%, CC74 +25 |
| Accent (>) | CC11 +25, CC74 +20 |
| Strong Accent/Marcato (^) | CC11 +30, CC74 +25 |
| Tenuto (-) | CC11 +5, full duration |
| Legato/Slur | CC64 = 127 (sustain on) |

#### Dynamic Mapping

Semantic dynamics (not just velocity):

| Dynamic | CC11 Value | Description |
|---------|------------|-------------|
| ppp | 20 | Very soft |
| pp | 35 | Soft |
| p | 50 | Piano |
| mp | 65 | Mezzo-piano |
| mf | 80 | Mezzo-forte (default) |
| f | 95 | Forte |
| ff | 110 | Very loud |
| fff | 127 | Maximum |

#### Intelligent Vibrato (CC1)

- Long notes (≥2 beats): CC1 = 64 (moderate vibrato)
- Medium notes (≥1 beat): CC1 = 48 (light vibrato)
- Short notes: CC1 = 0 (no vibrato)

#### Saxophone Breath (CC2)

For SWAM Saxophone, breath controller (CC2) is automatically:
- Linked to expression level (CC11)
- Reduced for staccato notes
- Increased for accented notes

### Step 5: Import to DAW

1. **Open your DAW** (Reaper, Cubase, Studio One, Logic, etc.)

2. **Create MIDI track**

3. **Load SWAM VST3**
   - SWAM Violin or SWAM Saxophone

4. **Import processed MIDI**
   - Drag from `midi_output/` folder
   - Or File → Import → MIDI

5. **Verify CC messages in MIDI editor:**
   - Open MIDI editor/piano roll
   - Look for CC lanes:
     - CC11 (Expression) - Should vary with dynamics
     - CC1 (Modulation/Vibrato) -  On sustained notes
     - CC74 (Brightness) - Higher on accented notes
     - CC64 (Sustain) - On during slurred passages
     - CC2 (Breath) - For saxophone only

6. **Play and enjoy!**

### Step 6: Fine-Tuning (Optional)

After import, you can manually adjust:

- **CC11 curves** - Draw custom expression shapes
- **CC1 depth** - Increase/decrease vibrato intensity
- **CC74 brightness** - Adjust tone color
- **Note timing** - Humanize or tighten rhythm

## Troubleshooting

### "Module 'music21' not found"
```bash
pip install music21
```

### No articulations detected

**Check in MuseScore:**
1. View → Show Articulations
2. Ensure articulations are visible on notes
3. Re-export MusicXML

**In verbose mode**, you should see:
```
Articulations detected:
  - staccato: X
  - accent: Y
```

If counts are 0, articulations weren't added in MuseScore.

### Articulations  sound wrong

**Check SWAM settings:**
1. Open SWAM plugin
2. MIDI tab → Ensure CC1, CC11, CC74, CC64 are enabled
3. Set response curves to linear or slight exponential

### Dynamics too extreme

Edit `config/swam_config.json` and adjust dynamic CC values:
```json
"dynamics": {
  "pp": 45,    // Increase from 35 for louder PP
  "ff": 100    // Decrease from 110 for quieter FF
}
```

## Comparison: MIDI vs MusicXML Approach

### Example: Accented Staccato Note

**MIDI Export Result:**
- Note with velocity 100
- Short duration (guessed)
- No articulation metadata
- **Script must guess:** "Is this staccato? Or just short?"

**MusicXML Export Result:**
- Note with explicit "staccato" + "accent" articulations
- Duration as written
- Dynamic marking (e.g., "f") preserved
- **Script knows exactly:** Apply staccato (CC11 -20, shorten) AND accent (CC11 +25, CC74 +20)

### Result in SWAM:
- **MusicXML:** Clear, emphasized attack with brightness → Realistic
- **MIDI:** Ambiguous, possibly wrong interpretation → Less realistic

## Advanced Techniques

### Layering Articulations

MuseScore allows multiple articulations on one note:
- Staccato + Accent = Short, emphasized note
- Tenuto + Accent = Full-length, emphasized note

The script intelligently combines CC effects.

### Expression Text

Add expression text in MuseScore (Ctrl+T):
- "vibrato" - Adds CC1 even on shorter notes
- "dolce" - Could reduce CC74 (brightness)
- "marcato" - Recognized as strong accent

(Some expressions automatically mapped, extensible in code)

### Crescendo/Diminuendo

Place hairpin wedges in MuseScore:
- Script detects start and end points
- Generates smooth CC11 ramp
- More natural than per-note velocity changes

## Next Steps

- Experiment with different articulation combinations
- Create custom SWAM presets for different styles (classical, contemporary, jazz)
- Adjust CC mappings in `config/swam_config.json` for your taste
- Build a library of MusicXML templates for common patterns

## Tips for Best Results

1. **Be explicit in MuseScore** - Don't rely on playback defaults, mark everything
2. **Use slurs generously** - They control legato (CC64)
3. **Mark ALL dynamics** - Even if "obvious", scripts need them
4. **Test incrementally** - Start with 8-bar phrase before processing full piece
5. **Listen in MuseScore first** - If it doesn't sound good there, fix notation first
6. **Save variations** - Export multiple CC mappings (light vs heavy vibrato) and blend in DAW

---

**Questions or issues?** Check the main README.md or open an issue on GitHub.

Happy composing with MusicXML! 🎼🎻🎷
