# Violin Test File - MARKED VERSION - Reference Guide

**File:** `violintest_marked.xml`  
**MIDI Output:** `violintest_marked_violin_swam.mid`

This file contains clearly marked sections to help identify exactly where audio/score inconsistencies occur.

---

## 📍 SECTION MARKERS

### MARKER 1: ASCENDING ACCENTS (Measure 1)
- **Notes:** C5 → D5 → E5 → F5
- **Direction:** **ASCENDING** (going UP)
- **Articulation:** Accent on each note
- **Dynamic:** mf (medium loud)
- **What to hear:** Four distinct accented notes, pitch rising steadily

---

### MARKER 2: ASCENDING STACCATO (Measure 2)
- **Notes:** G5 → A5 → B5 → C6
- **Direction:** **ASCENDING** (going UP to high C)
- **Articulation:** Staccato (short/detached)
- **Dynamic:** mf (continuing)
- **What to hear:** Four short notes, pitch rising to highest note

---

### MARKER 3: DESCENDING STACCATO (Measure 3)
- **Notes:** C6 → B5 → A5 → G5
- **Direction:** **DESCENDING** (going DOWN from high C)
- **Articulation:** Staccato (short/detached)
- **Dynamic:** f (loud - sudden change)
- **What to hear:** Four short notes, pitch falling, louder than previous

---

### MARKER 4: OCTAVE JUMP TEST (Measure 4)
- **Notes:** C5 → C6 → C5 → C6
- **Direction:** **JUMPING** (octave up/down pattern)
- **Articulation:** Accent on each
- **Dynamic:** f (loud)
- **What to hear:** Low-High-Low-High pattern, very distinct octave jumps

---

### MARKER 5: LEGATO SLUR ASCENDING (Measure 5)
- **Notes:** D5 → E5 → F5 → G5
- **Direction:** **ASCENDING** (going UP, smoothly connected)
- **Articulation:** Legato slur (one bow, connected)
- **Dynamic:** mp (soft - sudden change)
- **What to hear:** Four notes smoothly connected, no gaps, softer

---

### MARKER 6: TREMOLO (Measure 6)
- **Notes:** A5 repeated 4 times (in score)
- **Direction:** **SAME PITCH** (sustained notes)
- **Articulation:** Tremolo (bow shaking via SWAM built-in CC60)
- **Dynamic:** mp (soft)
- **What to hear:** SWAM's built-in fast bow tremolo effect on sustained A5 notes
- **MIDI Output:** 4 quarter notes with **CC60=127 (fast tremolo speed)** active during each note
- **Technical:** Uses SWAM CC60 tremolo control: 0=OFF, low values=slow, high values=fast (continuous control)

---

### MARKER 7: CRESCENDO (Measure 7)
- **Notes:** E5 → F5 → G5 → A5
- **Direction:** **ASCENDING** (going UP)
- **Articulation:** None (plain notes)
- **Dynamic:** Crescendo (getting gradually louder)
- **What to hear:** Smooth pitch rise with volume increasing

---

### MARKER 8: DIMINUENDO (Measure 8)
- **Notes:** A5 → G5 → F5 → E5
- **Direction:** **DESCENDING** (going DOWN - mirror of M7)
- **Articulation:** None (plain notes)
- **Dynamic:** f → diminuendo (getting softer)
- **What to hear:** Smooth pitch fall with volume decreasing

---

### MARKER 9: FINISH (Measure 9)
- **Notes:** G5 (whole note, 4 beats)
- **Direction:** **SUSTAINED**
- **Articulation:** None
- **Dynamic:** p (quiet)
- **What to hear:** Long quiet note ending the piece

---

## 🔍 DIAGNOSIS CHECKLIST

Use this checklist to verify playback:

- [ ] **M1:** Notes go UP (C→D→E→F)?
- [ ] **M2:** Notes go UP (G→A→B→C6)? Should end on **highest note** of piece
- [ ] **M3:** Notes go DOWN (C6→B→A→G)? Should start from **same high C** as M2
- [ ] **M4:** Clear octave JUMPS (low-high-low-high)?
- [ ] **M5:** Notes connected smoothly (legato)?
- [ ] **M6:** Rapid tremolo on repeated A5?
- [ ] **M7:** Volume increases (crescendo)?
- [ ] **M8:** Volume decreases (diminuendo)?
- [ ] **M9:** Long final note?

---

## 🚨 COMMON ISSUES TO CHECK

1. **Reversed direction:** If any ascending section plays descending (or vice versa), note the measure number
2. **Tremolo timing:** If M6 doesn't sound like rapid repetition, there's a tremolo parsing issue
3. **Octave errors:** If M4 doesn't have clear high/low jumps, octaves aren't parsing correctly
4. **Dynamic response:** If M3 isn't noticeably louder than M2, dynamics may not be working
5. **Legato vs staccato:** Compare M2 (short) vs M5 (smooth) - articulations should be clearly different

---

## 📝 REPORTING ISSUES

When reporting inconsistencies, use this format:

```
MARKER X (Measure Y): [Description]
Expected: [What should happen]
Actual: [What you hear]
```

Example:
```
MARKER 2 (Measure 2): Staccato direction wrong
Expected: G5 → A5 → B5 → C6 (ascending to high C)
Actual: Notes seem to descend instead
```
