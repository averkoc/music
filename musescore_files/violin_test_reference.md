# ⚠️ DEPRECATED - Use violin_reference_test.xml Instead

**This documentation is outdated. Please use the new canonical test file:**

📄 **File:** `violin_reference_test.xml`  
📖 **Guide:** [violin_reference_test_GUIDE.md](violin_reference_test_GUIDE.md)

The new reference file includes:
- ✅ All features from this file
- ✅ Visual markers for easy following
- ✅ Additional articulations (tremolo, pizzicato)
- ✅ Better organization (14 measures)
- ✅ Comprehensive documentation

---

# OLD DOCUMENTATION BELOW (Archived)

# Violin.xml - Feature Demonstration Reference

A 12-bar test file showcasing all supported SWAM articulations, dynamics, and techniques.

## Measure-by-Measure Breakdown

### Measure 1: Accents with pp dynamic
- **Dynamic**: pp (pianissimo, CC11 ≈ 35)
- **Articulation**: Accent on all four quarter notes
- **Notes**: G4, A4, B4, C5

### Measure 2: Staccato with mf dynamic
- **Dynamic**: mf (mezzo-forte, CC11 ≈ 80)
- **Articulation**: Staccato on all notes (short, detached)
- **Notes**: D5, E5, F5, G5

### Measure 3: Tenuto and Strong Accents
- **Articulations**: 
  - Tenuto on first two notes (sustained, full value)
  - Strong accents (marcato) on last two notes
- **Notes**: A5, G5, F5, E5

### Measure 4: Crescendo Hairpin
- **Dynamic Change**: mp → f (crescendo over 4 beats)
- **Start**: mp (CC11 ≈ 65)
- **End**: f (CC11 ≈ 95)
- **Notes**: D5, C5, B4, A4

### Measure 5: Slurred Legato Passage
- **Articulation**: Slur connecting all four notes
- **Effect**: Smooth, connected with portamento (CC5 ≈ 40)
- **Notes**: G4, A4, B4, C5

### Measure 6: Diminuendo Hairpin
- **Dynamic Change**: f → p (diminuendo over 2 half notes)
- **Start**: f (CC11 ≈ 95)
- **End**: p (CC11 ≈ 50)
- **Notes**: D5 (half), E5 (half)

### Measure 7: Glissando
- **Articulation**: Glissando (wavy line slide)
- **Effect**: Continuous pitch slide from C5 to G5
- **MIDI**: High portamento (CC5 ≈ 110), 50% note overlap
- **Notes**: C5 → G5 (both half notes)

### Measure 8: Vibrato with ff dynamic
- **Dynamic**: ff (fortissimo, CC11 ≈ 110)
- **Articulation**: Wavy line (vibrato marking)
- **Effect**: CC1 modulation ramping to ~64 after delay
- **Notes**: A5 (whole note)

### Measure 9: Sul Ponticello (continues vibrato)
- **Technique**: "sul pont." - bow near bridge
- **Effect**: Bright, glassy tone (CC21 ≈ 115)
- **Vibrato**: Continues from previous measure
- **Notes**: E5, F5, G5, A5 (quarter notes)

### Measure 10: Sul Tasto with p dynamic
- **Dynamic**: p (piano, CC11 ≈ 50)
- **Technique**: "sul tasto" - bow over fingerboard
- **Effect**: Soft, flute-like tone (CC21 ≈ 20)
- **Notes**: G5, F5, E5, D5 (quarter notes)

### Measure 11: Mixed Articulation Showcase
- **Dynamic**: mf (CC11 ≈ 80)
- **Articulations**:
  - Beat 1: Staccato (C5)
  - Beat 2: Accent (D5)
  - Beats 3-4: Slurred eighth notes (E5, F5, G5, A5)

### Measure 12: Final Crescendo to fff
- **Dynamic Change**: Current → fff (crescendo)
- **End**: fff (CC11 ≈ 120)
- **Final Note**: G5 with fermata (hold)
- **Notes**: D5, E5, F5, G5

## Testing the File

### Process with MusicXML Script:
```bash
# DEPRECATED - Use violin_reference_test.xml instead
python scripts/process_musicxml.py musescore_files/violin_reference_test.xml
```

### Output Location:
# DEPRECATED - New file outputs to:
midi_output/violin_reference_test
midi_output/violin_violin_swam.mid
```

### Expected MIDI CC Events:
- **CC11** (Expression): Dynamic changes and crescendo/diminuendo ramps
- **CC1** (Modulation): Vibrato in measures 8-9
- **CC5** (Portamento): Slurs (measure 5) and glissando (measure 7)
- **CC21** (Bow Position): Sul ponticello (measure 9), sul tasto (measure 10)
- **CC64** (Sustain): Legato mode during slurs

### Key Features Demonstrated:
✅ All dynamic levels (pp, p, mp, mf, f, ff, fff)  
✅ Crescendo and diminuendo hairpins  
✅ Articulations: accent, staccato, tenuto, marcato  
✅ Legato/slur with portamento  
✅ Glissando with high portamento  
✅ Vibrato (wavy line)  
✅ String techniques: sul ponticello, sul tasto  
✅ Mixed rhythms: quarters, halves, eighths, whole notes  

## Presentation Notes

This file is ideal for demonstrating:
1. **Dynamic range** - From whisper-soft pp to blazing fff
2. **Articulation variety** - Short staccato to smooth legato
3. **Expressive techniques** - Glissando, vibrato, bow position changes
4. **SWAM CC mapping** - How MusicXML translates to continuous controllers
5. **Realistic performance** - Gradual dynamic changes, natural phrasing

The 12-bar format keeps the demo concise while covering all major features.
