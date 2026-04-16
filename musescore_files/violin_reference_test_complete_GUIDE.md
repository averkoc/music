# MuseScore Reference Test File - Complete Articulation Guide
## violin_reference_test_complete.mscz

**Purpose:** Comprehensive test file for all SWAM articulation implementations including new April 2026 enhancements.

**Status:** ✅ All techniques fully working (April 2026)
- Flautato, col legno, and scratch now use stateful technique tracking
- Techniques are detected from measure-level text directions
- Techniques persist across notes until explicitly changed

**Time Signature:** 4/4  
**Tempo:** 120 BPM  
**Total Measures:** 24  
**Instrument:** Violin

---

## Measure-by-Measure Creation Guide

### MEASURE 1: SETUP & PLAIN NOTES
**Marker:** "M1: PLAIN NOTES"  
**Dynamic:** mp  
**Notes:** C5, D5, E5, F5 (4 quarter notes)  
**Articulations:** None (test default behavior)

**Purpose:** Baseline for natural bow dynamics and expression

---

### MEASURE 2: STACCATO
**Marker:** "M2: STACCATO"  
**Dynamic:** mf  
**Notes:** G5, A5, B5, C6 (4 quarter notes)  
**Articulations:** Staccato dot (•) on all notes  

**Tests:** 
- CC11 spike + 35% duration
- Sharp note-off velocity (110)
- Bow force variation

---

### MEASURE 3: STACCATISSIMO
**Marker:** "M3: STACCATISSIMO"  
**Dynamic:** f  
**Notes:** D6, C6, B5, A5 (4 quarter notes)  
**Articulations:** Staccatissimo wedge (▼) on all notes  

**Tests:**
- CC11 spike + 20% duration
- Very sharp note-off velocity (120)

---

### MEASURE 4: TENUTO
**Marker:** "M4: TENUTO"  
**Dynamic:** mp  
**Notes:** G5, F5, E5, D5 (4 quarter notes)  
**Articulations:** Tenuto line (−) on all notes  

**Tests:**
- Full duration sustain
- Gentle note-off velocity (30)

---

### MEASURE 5: ACCENT
**Marker:** "M5: ACCENT"  
**Dynamic:** mf  
**Notes:** C5, E5, G5, C6 (4 quarter notes)  
**Articulations:** Accent (>) on all notes  

**Tests:**
- CC11 peak at onset (110)
- Moderate note-off velocity (80)
- Bow force increase

---

### MEASURE 6: MARCATO (MARTELÉ)
**Marker:** "M6: MARCATO (MARTELÉ)"  
**Dynamic:** f  
**Notes:** D6, B5, G5, E5 (4 quarter notes)  
**Articulations:** Marcato (^) on all notes  

**Tests:**
- CC11 peak (120)
- **CC20 bow pressure envelope: spike 83-102 → decay to 64**
- Strong bow attack then release

---

### MEASURE 7: LEGATO SLUR (CC64 TEST)
**Marker:** "M7: LEGATO SLUR"  
**Dynamic:** p  
**Notes:** C5, D5, E5, F5, G5, A5, B5, C6 (8 eighth notes)  
**Articulations:** Single slur connecting all notes  

**Tests:**
- **CC64 (sustain) = 127 activated**
- High velocity (90+) for overlapped notes
- 20% note overlap
- Smooth legato connection

---

### MEASURE 8: PORTAMENTO (GLISSANDO)
**Marker:** "M8: PORTAMENTO"  
**Dynamic:** mf  
**Notes:** C6, G5 (half notes)  
**Articulations:** Glissando line between them  

**Tests:**
- CC5 = 110 (high portamento)
- 50% note overlap
- Seamless pitch slide

---

### MEASURE 9: CRESCENDO
**Marker:** "M9: CRESCENDO"  
**Dynamic:** pp → ff  
**Notes:** C5, D5, E5, F5 (4 quarter notes)  
**Articulations:** Crescendo hairpin (<) over all notes  

**Tests:**
- Exponential CC11 ramp
- Dynamic transition from pp (20) to ff (110)

---

### MEASURE 10: DIMINUENDO
**Marker:** "M10: DIMINUENDO"  
**Dynamic:** ff → pp  
**Notes:** F5, E5, D5, C5 (4 quarter notes)  
**Articulations:** Diminuendo hairpin (>) over all notes  

**Tests:**
- Exponential CC11 ramp down
- Dynamic transition from ff (110) to pp (20)

---

### MEASURE 11: VIBRATO
**Marker:** "M11: VIBRATO"  
**Dynamic:** mp  
**Text:** "vibrato" above staff  
**Notes:** A5 (whole note)  
**Articulations:** None (text triggers vibrato)  

**Tests:**
- Delayed vibrato onset
- CC1 (modulation) ramp
- CC17 (vibrato rate) control
- Pitch-dependent vibrato parameters

---

### MEASURE 12: TREMOLO
**Marker:** "M12: TREMOLO"  
**Dynamic:** mf  
**Notes:** E5, E5, D5, D5 (4 quarter notes)  
**Articulations:** Three-stroke tremolo on all notes  

**Tests:**
- CC60 = 85 (tremolo speed)
- Automatic tremolo reset after note

---

### MEASURE 13: PIZZICATO
**Marker:** "M13: PIZZICATO"  
**Text:** "pizz." above staff  
**Dynamic:** mf  
**Notes:** C5, D5, E5, F5 (4 quarter notes)  
**Articulations:** Pizzicato marking on all notes  

**Tests:**
- **CC61 = 50 (pizzicato mode)**
- Plucked string sound
- Short note duration

---

### MEASURE 14: COL LEGNO
**Marker:** "M14: COL LEGNO"  
**Text:** "col legno" above staff  
**Dynamic:** f  
**Notes:** G5, A5, B5, C6 (4 quarter notes)  
**Articulations:** Manual text (MuseScore doesn't have native col legno)  

**Tests:**
- **CC61 = 90 (col legno mode)**
- Struck-with-wood sound
- Return to arco after measure

---

### MEASURE 15: FLAUTATO
**Marker:** "M15: FLAUTATO"  
**Text:** "flautato" above staff  
**Dynamic:** pp  
**Notes:** D6, C6, B5, A5 (4 quarter notes)  
**Articulations:** Manual text  

**Tests:**
- **CC20 = 15 (very light bow pressure)**
- Airy, flute-like tone
- Delicate sound

---

### MEASURE 16: SCRATCH
**Marker:** "M16: SCRATCH"  
**Text:** "scratch" above staff  
**Dynamic:** ff  
**Notes:** C5, E5, G5, C6 (4 quarter notes)  
**Articulations:** Manual text  

**Tests:**
- **CC20 = 125 (maximum bow pressure)**
- Harsh, gritty tone
- High expression boost

---

### MEASURE 17: SUL PONTICELLO
**Marker:** "M17: SUL PONTICELLO"  
**Text:** "sul pont." above staff  
**Dynamic:** mf  
**Notes:** E5, F5, G5, A5 (4 quarter notes)  
**Articulations:** Manual text  

**Tests:**
- **CC21 = 115 (bow near bridge)**
- Bright, glassy tone
- Intense overtones

---

### MEASURE 18: SUL TASTO
**Marker:** "M18: SUL TASTO"  
**Text:** "sul tasto" above staff  
**Dynamic:** p  
**Notes:** A5, G5, F5, E5 (4 quarter notes)  
**Articulations:** Manual text  

**Tests:**
- **CC21 = 15 (bow over fingerboard)**
- Dark, soft tone
- Muted overtones

---

### MEASURE 19: SPICCATO
**Marker:** "M19: SPICCATO"  
**Text:** "spiccato" above staff  
**Dynamic:** mf  
**Notes:** C5, D5, E5, F5, G5, A5, B5, C6 (8 eighth notes)  
**Articulations:** Manual text  

**Tests:**
- CC11 spike + 40% duration
- Light bow force (50-75)
- Bow position toward bridge (72)
- Bouncing bow effect

---

### MEASURE 20: DÉTACHÉ
**Marker:** "M20: DÉTACHÉ"  
**Text:** "détaché" above staff  
**Dynamic:** mf  
**Notes:** G5, F5, E5, D5 (4 quarter notes, separated, not slurred)  
**Articulations:** Manual text (notes are separate, not connected)  

**Tests:**
- Sustain pedal state management
- Separated bow strokes with connection
- No note overlap

---

### MEASURE 21: MIXED DYNAMICS
**Marker:** "M21: MIXED DYNAMICS"  
**Dynamic:** p, mf, f, ff (one per note)  
**Notes:** C5(p), E5(mf), G5(f), C6(ff) (4 quarter notes)  
**Articulations:** None  

**Tests:**
- Rapid dynamic changes
- CC11 smooth transitions
- Expression variety

---

### MEASURE 22: MIXED ARTICULATIONS
**Marker:** "M22: MIXED ARTICULATIONS"  
**Dynamic:** mf  
**Notes:** 
- C5 quarter (staccato)
- D5 quarter (accent)
- E5, F5 (eighth notes with slur)
- G5 half note (tenuto)  

**Tests:**
- Multiple articulation handling
- Articulation switching
- Combined effects

---

### MEASURE 23: CHROMATIC PASSAGE
**Marker:** "M23: CHROMATIC"  
**Dynamic:** mp crescendo to f  
**Notes:** C5, C#5, D5, D#5, E5, F5, F#5, G5 (8 eighth notes)  
**Articulations:** Slur over all  

**Tests:**
- Legato in chromatic context
- Metrical emphasis
- Interval-aware portamento disabled (slurred)

---

### MEASURE 24: FINALE
**Marker:** "M24: FINALE"  
**Dynamic:** fff  
**Notes:** C6 (whole note)  
**Articulations:** Fermata  

**Tests:**
- Maximum expression
- Natural vibrato on long note
- Clean ending

---

## Creation Steps in MuseScore

### Step 1: Create New Score
1. File → New
2. Choose: Solo → Violin
3. Set: 24 measures, 4/4 time, 120 BPM
4. Key: C major

### Step 2: Add All Notes
Follow measure-by-measure guide above for note entry

### Step 3: Add Dynamics
- Use Palette → Dynamics
- Or press shortcuts (pp, p, mp, mf, f, ff, fff)

### Step 4: Add Articulations
- Staccato: Select note → Palette → Articulations → Staccato
- Accent: Select note → click accent (>)
- Slur: Select first note → "S" key → select last note
- Tremolo: Select note → Palette → Tremolo
- Pizzicato: Right-click note → Note Properties → Pizzicato

### Step 5: Add Text Markers
For each measure:
1. Right-click start of measure (above staff)
2. Add → Text → System Text (Ctrl+Shift+T)
3. Type marker (e.g., "M1: PLAIN NOTES")
4. Make bold if desired

### Step 6: Add Expression Text
For text-based articulations (flautato, scratch, etc.):
1. Select first note in measure
2. Add → Text → Staff Text (Ctrl+T)
3. Type articulation name

### Step 7: Export
1. File → Save as `violin_reference_test_complete.mscz`
2. File → Export → MusicXML
3. Save as `violin_reference_test_complete.xml`

---

## Processing Command

```bash
python scripts/process_musicxml.py musescore_files/violin_reference_test_complete.xml -i violin -o midi_output/test_complete.mid -v
```

---

## What This Tests

### SWAM Manual-Based Implementations (April 2026)
✅ Legato with CC64 sustain pedal + high velocity  
✅ Martelé with bow pressure envelope (CC20 spike)  
✅ Flautato (CC20 = 15)  
✅ Scratch (CC20 = 125)  
✅ Sul Ponticello (CC21 = 115)  
✅ Sul Tasto (CC21 = 15)  
✅ Spiccato (partial - needs BowLift)  
✅ Détaché (sustain pedal management)  

### Core Articulations
✅ Staccato, Staccatissimo, Tenuto  
✅ Accent, Strong Accent, Marcato  
✅ Slur, Legato, Portamento/Glissando  
✅ Vibrato (delayed onset, pitch-dependent)  
✅ Tremolo (CC60)  
✅ Pizzicato (CC61 = 50)  
✅ Col Legno (CC61 = 90)  

### Dynamic Features
✅ Crescendo/Diminuendo with exponential curves  
✅ Dynamic range (pp to fff)  
✅ Metrical emphasis  
✅ Expression transitions  

---

## Expected Output Characteristics

**Legato Sections:** Smooth CC64 transitions, overlapped notes, no portamento  
**Martelé:** Sharp attack with audible bow pressure spike, then smooth sustain  
**Flautato:** Weak, airy attack with minimal pressure  
**Scratch:** Harsh, prominent bow noise with maximum pressure  
**Sul Ponticello:** Bright, glassy tone with enhanced harmonics  
**Sul Tasto:** Soft, dark tone with muted overtones  
**Pizzicato:** Plucked attack, short decay  
**Col Legno:** Percussive, wooden attack  

---

## Tips

- **Spacing:** One articulation style per measure prevents overlap
- **Clarity:** Clear markers make it easy to identify which section is which
- **Isolation:** Test each articulation individually in SWAM before mixing
- **Comparison:** Export both with and without humanization for comparison
- **Listen:** Import into DAW with SWAM Violin VST3 to hear results

---

## Troubleshooting

**Text articulations not detected (flautato, col legno, scratch):**
- Ensure text is Staff Text (Ctrl+T), not System Text
- Text can be anywhere in the measure - detection uses measure-level `<direction>` elements
- Technique persists across all notes until changed or cleared with "arco"
- Check spelling matches keywords in articulation_detector.py
- **Fixed April 2026:** Techniques now use stateful tracking instead of per-note detection

**Slurs not working:**
- Ensure slur connects notes (not ties)
- Check that notes actually overlap in MIDI output

**Dynamics not changing:**
- Ensure dynamic markings are from Dynamics palette
- Check they're attached to notes, not floating

**Pizzicato/Col Legno not switching:**
- Add "pizzicato" or "col legno" as Staff Text in the measure
- Alternatively mark articulation in Note Properties (if available)
- Check MIDI output has CC61 messages (use check_flautato_collegno.py script)
- Technique persists until cleared with "arco" text

---

This comprehensive test file provides complete coverage of all articulation features with proper spacing for clear audio analysis.
