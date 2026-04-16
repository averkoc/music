# 🎻 SWAM Violin Reference Test - Complete Guide

**File:** `violin_reference_test.xml`  
**MIDI Output:** `violin_reference_test_violin_swam.mid`  
**Duration:** 14 measures (approx. 56 seconds at 120 BPM)

This is the **canonical test file** for the MuseScore to SWAM workflow. It demonstrates all supported articulations, dynamics, and expressive techniques with clear visual markers.

---

## 🎯 Purpose

This file serves three critical functions:
1. **Testing** - Verify that all SWAM CC mappings work correctly
2. **Demonstration** - Showcase what's possible with SWAM processing
3. **Reference** - Follow along in MuseScore Studio while listening to MIDI playback

---

## 📋 Complete Feature List (14 Measures)

### MARKER 1: ACCENTS (pp)
- **Notes:** G4 → A4 → B4 → C5 (ascending)
- **Dynamic:** pp (pianissimo, CC11 ≈ 35)
- **Articulation:** Accent (>) on each note
- **SWAM Effect:** Velocity boost + brief CC11 spike
- **Listen for:** Soft but emphasized attacks

### MARKER 2: STACCATO (mf)
- **Notes:** D5 → E5 → F5 → G5 (ascending)
- **Dynamic:** mf (mezzo-forte, CC11 ≈ 80)
- **Articulation:** Staccato (.) - short/detached
- **SWAM Effect:** 50% duration reduction
- **Listen for:** Short, bouncy notes with clear separation

### MARKER 3: TENUTO + MARCATO
- **Notes:** A5 → G5 (tenuto) → F5 → E5 (marcato descending)
- **Articulation:** Tenuto (-) first two, strong accent (^) last two
- **SWAM Effect:** 
  - Tenuto: Full note length sustained
  - Marcato: Heavy attack with CC11 boost
- **Listen for:** Smooth sustained notes, then powerful accents

### MARKER 4: CRESCENDO
- **Notes:** D5 → E5 → F5 → G5 (ascending)
- **Dynamic Change:** mp → f (crescendo hairpin)
- **SWAM Effect:** Exponential CC11 ramp from 65 to 95
- **Listen for:** Gradual volume increase over 4 beats

### MARKER 5: LEGATO SLUR
- **Notes:** G4 → A4 → B4 → C5 (ascending, connected)
- **Articulation:** Slur line connecting all notes
- **SWAM Effect:** 
  - CC64 = 127 (sustain/legato mode ON)
  - CC5 ≈ 40 (portamento for smooth transitions)
  - 15% note overlap
- **Listen for:** Smooth, connected phrase with subtle pitch slides

### MARKER 6: DIMINUENDO
- **Notes:** D5 (half) → E5 (half)
- **Dynamic Change:** f → p (diminuendo hairpin)
- **SWAM Effect:** Exponential CC11 ramp from 95 to 50
- **Listen for:** Gradual volume decrease over 4 beats

### MARKER 7: GLISSANDO
- **Notes:** C5 → G5 (perfect fifth leap)
- **Articulation:** Wavy line glissando
- **SWAM Effect:**
  - CC5 ≈ 110 (high portamento time)
  - 50% note overlap
  - Continuous pitch slide
- **Listen for:** Smooth "siren" pitch sweep from C to G

### MARKER 8: VIBRATO (ff)
- **Notes:** A5 (whole note, 4 beats)
- **Dynamic:** ff (fortissimo, CC11 ≈ 110)
- **Articulation:** Wavy line (vibrato marking)
- **SWAM Effect:**
  - CC1 (modulation) ramps to ~64 with 200ms delay
  - Exponential ramp for natural onset
- **Listen for:** Loud sustained note with warm, expressive vibrato

### MARKER 9: SUL PONTICELLO
- **Notes:** E5 → F5 → G5 → A5 (ascending)
- **Technique:** "sul pont." - bow near bridge
- **SWAM Effect:**
  - CC21 ≈ 115 (bow position near bridge)
  - Vibrato continues from previous measure
- **Listen for:** Bright, glassy, "whistling" tone quality

### MARKER 10: SUL TASTO (p)
- **Notes:** G5 → F5 → E5 → D5 (descending)
- **Dynamic:** p (piano, CC11 ≈ 50)
- **Technique:** "sul tasto" - bow over fingerboard
- **SWAM Effect:**
  - CC21 ≈ 20 (bow position over fingerboard)
  - Vibrato stops
- **Listen for:** Soft, flute-like, "breathy" tone

### MARKER 11: TREMOLO
- **Notes:** A5 → A5 → G5 → F5 (descending)
- **Dynamic:** mp (CC11 ≈ 60)
- **Articulation:** Tremolo slashes (rapid bow changes)
- **SWAM Effect:**
  - CC60 = 127 (SWAM's built-in fast tremolo)
  - Continuous control during each note
- **Listen for:** Fast, shimmering bow oscillation

### MARKER 12: PIZZICATO
- **Notes:** E5 → D5 → C5 → B4 (descending)
- **Technique:** "pizz." - plucked strings
- **SWAM Effect:**
  - Very short note duration (80% reduction)
  - Sharp attack, quick decay
- **Listen for:** Plucked, "guitar-like" sound

### MARKER 13: MIXED ARTICULATIONS
- **Notes:** C5 (staccato), D5 (accent), E-F-G-A (slurred eighths)
- **Dynamic:** mf (CC11 ≈ 80)
- **Technique:** "arco" returns to bowed playing
- **Articulation:** Combination showcase
- **Listen for:** Variety - short, accented, then smooth legato run

### MARKER 14: FINAL CRESCENDO
- **Notes:** D5 → E5 → F5 → G5 (ascending)
- **Dynamic Change:** Current → fff (crescendo to triple forte)
- **Effect:** CC11 ramps to 120 (maximum)
- **Final Note:** G5 with fermata (hold)
- **Listen for:** Powerful dramatic finish, pause on final note

---

## 🎵 How to Use This File

### Option A: Import XML into MuseScore (Recommended)

If the XML file doesn't open directly in MuseScore Studio:

1. **Try importing:** File → Open → Select `violin_reference_test.xml`
2. **If successful:** Save as `violin_reference_test.mscz` for future use
3. **If it fails:** See [IMPORT_INSTRUCTIONS.md](IMPORT_INSTRUCTIONS.md) for manual creation steps

### Option B: Process to MIDI Directly

You can process the XML file even if MuseScore can't open it:

### 1. Process MusicXML to MIDI
```bash
python scripts/process_musicxml.py musescore_files/violin_reference_test.xml
```

### 2. Output Location
```
midi_output/violin_reference_test_violin_swam.mid
```

### 3. Follow Along in MuseScore Studio
1. Open `violin_reference_test.xml` in MuseScore Studio
2. Start the HTML player with the generated MIDI:
   ```bash
   python start_player.py
   ```
3. Load `violin_reference_test_violin_swam.mid` in the player
4. **Watch the score while listening** - markers show exactly where you are

### 4. Verify in Your DAW
- Import MIDI into Ableton/Reaper/etc.
- Load SWAM Violin VST3 on the MIDI track
- **Check CC lanes:**
  - CC11 (Expression) automation
  - CC1 (Modulation/Vibrato)
  - CC5 (Portamento)
  - CC21 (Bow Position)
  - CC60 (Tremolo)
  - CC64 (Sustain/Legato)

---

## 🔍 Expected MIDI CC Patterns

| Measure | Primary CCs | Pattern |
|---------|-------------|---------|
| 1 | CC11 | Steady pp (~35) with brief spikes for accents |
| 2 | CC11 | Steady mf (~80) |
| 3 | CC11 | Boost for marcato articulations |
| 4 | CC11 | Exponential ramp 65→95 |
| 5 | CC64, CC5 | Sustain ON (127), portamento ~40 |
| 6 | CC11 | Exponential ramp 95→50 |
| 7 | CC5, CC64 | High portamento (110), sustain ON |
| 8 | CC11, CC1 | High expression (110), vibrato onset |
| 9 | CC21, CC1 | Sul pont (115), vibrato continues |
| 10 | CC21 | Sul tasto (20), vibrato stops |
| 11 | CC60 | Tremolo ON (127) for each note |
| 12 | - | Short note durations (pizzicato) |
| 13 | CC64, CC5 | Mixed: staccato + accent + slur |
| 14 | CC11 | Final crescendo ramp to 120 |

---

## ✅ Feature Coverage Checklist

### Dynamics (CC11)
- [x] pp, p, mp, mf, f, ff, fff (7 levels)
- [x] Crescendo hairpin (exponential ramp)
- [x] Diminuendo hairpin (exponential ramp)

### Articulations
- [x] Accent (>)
- [x] Staccato (.)
- [x] Tenuto (-)
- [x] Marcato/Strong Accent (^)
- [x] Slur/Legato (curved line)

### Expressive Techniques
- [x] Glissando (wavy line slide)
- [x] Vibrato (wavy line, CC1 modulation)
- [x] Portamento (CC5 with slurs)
- [x] Tremolo (rapid bow, CC60)

### String-Specific Techniques
- [x] Sul Ponticello (bow near bridge, CC21 high)
- [x] Sul Tasto (bow over fingerboard, CC21 low)
- [x] Pizzicato (plucked strings)
- [x] Arco (return to bowed)

### Rhythmic Variety
- [x] Quarter notes
- [x] Half notes
- [x] Whole notes
- [x] Eighth notes
- [x] Fermata (hold)

---

## 🚀 What's New vs. Previous Test Files

This reference file **consolidates and enhances** all previous test files:

### From `violin.xml`:
✅ All 12 original measures  
✅ Dynamics and articulations  
✅ Sul ponticello/tasto  
✅ Professional structure  

### From `violintest_marked.xml`:
✅ Clear visual markers (MARKER 1, MARKER 2, etc.)  
✅ Tremolo demonstration  
✅ Easier to follow along  

### New Additions:
✅ Pizzicato (measure 12)  
✅ Better organization (14 measures total)  
✅ More complete documentation  
✅ Bold marker text at 14pt font (visible in MuseScore)  

---

## 🎓 Educational Use

This file is perfect for:
- **Learning SWAM** - Hear what each articulation does
- **Teaching workflows** - Demonstrate MusicXML → MIDI → SWAM
- **Debugging** - Isolate which features work/don't work
- **Comparing outputs** - A/B test different processing versions

---

## 📝 Notes for Developers

- **divisions=480** (480 ticks/quarter) for precise timing
- **Unique slur numbers** prevent overlap conflicts
- **Proper wavy-line start/stop** for vibrato boundaries
- **Dynamic sound values** match expected CC11 levels
- **Articulation priority** handled by mapper (staccato overrides tenuto, etc.)

---

## 🔄 Keeping This File Updated

As new features are added to the SWAM mapper:
1. Add a new MARKER measure
2. Update this guide
3. Reprocess and verify output
4. Keep this as the single source of truth

**Do not create duplicate test files!** Update this one instead.

---

## 🆘 Troubleshooting

**Problem:** Text markers don't show in MuseScore  
**Solution:** Ensure you're viewing in Page View (not Continuous)

**Problem:** MIDI output missing certain CCs  
**Solution:** Check `swam_config.json` - some CCs may be disabled

**Problem:** Tremolo sounds wrong  
**Solution:** Verify your SWAM version supports CC60 tremolo control

**Problem:** Can't follow along with playback  
**Solution:** Use MuseScore's built-in playback OR the HTML player simultaneously

---

**Last Updated:** 2026-04-16  
**Test File Version:** 1.0  
**Replaces:** `violin.xml`, `violintest.xml`, `violintest_marked.xml`
