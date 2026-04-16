# SWAM Violin Parameters Reference

Complete reference of SWAM Solo Strings parameters from official manual (v2.0) and discovered values.

## Currently Mapped Parameters

| Parameter | CC# | Range | Description | Implementation |
|-----------|-----|-------|-------------|----------------|
| **Expression** | CC11 | 0-127 | Dynamic level/volume | ✅ Fully implemented |
| **Modulation** | CC1 | 0-127 | Vibrato depth | ✅ Implemented (capped at 110) |
| **Vibrato Rate** | CC17 | 0-127 | Vibrato speed | ✅ Implemented |
| **Portamento Time** | CC5 | 1-127 | Pitch slide duration | ✅ Implemented |
| **Bow Force** | CC20 | 0-127 | Bow pressure | ✅ Implemented |
| **Bow Position** | CC21 | 0-127 | Sul tasto ↔ Sul ponticello | ✅ Implemented |
| **Bow Mode** | CC61 | 0-127 | Arco/Pizzicato/Col Legno | ✅ **NEWLY IMPLEMENTED (April 2026)** |
| **Sustain Pedal** | CC64 | 0/127 | Legato/sustain mode | ✅ Implemented |
| **Harmonics** | CC74 | 0-127 | Brightness/tone color | ✅ Implemented |
| **Tremolo** | CC60 | 0-127 | Tremolo speed (0=off) | ✅ Implemented |
| **Main Volume** | CC7 | 0-127 | Channel volume | ✅ Implemented |
| **Pan** | CC10 | 0-127 | Stereo position | ✅ Implemented |

## Unmapped Parameters (To Be Implemented)

### Core Articulation Controls

| Parameter | Mapped To | Values/Modes | Description | Status |
|-----------|-----------|--------------|-------------|--------|
| **BowLift** | CC?? or KeySwitch | On String / Off String | Controls whether bow leaves string between notes | 🔍 **To discover** |
| **NoteOff Sust.** | CC?? or KS G | Hold / Acc. / Fade | Controls note release behavior with sustain pedal | 🔍 **To discover** |
| **Alt.Fing** | CC?? or KS D# | Positions | Alternative fingering/string selection | 🔍 **To discover** |
| **Bow Mode** | **CC61** | Normal / Pizz / Col Legno | Playing technique mode | ✅ **IMPLEMENTED (April 2026)** |

### Advanced Controls

| Parameter | Mapped To | Range/Modes | Description | Status |
|-----------|-----------|-------------|-------------|--------|
| **Port/Leg Speed&Thresh** | CC?? | 0-127 | Threshold between portamento and legato | 🔍 To discover |
| **Dynamic Transit.** | CC?? | 0-127 | Legato transition quality | 🔍 To discover |
| **Portam. Split Ratio** | Setting | 0-100% | Split point for cross-string portamento | ⚙️ Internal setting |
| **Tremolo Mode** | Setting | Slow / Fast / Sync / Sync+Acc | Auto-tremolo behavior | ⚙️ Internal setting |
| **Manual Trem/BowC KS** | KeySwitch C# | Trem / BowChange | Manual tremolo trigger | ⚙️ KeySwitch only |
| **Gesture Mode** | Setting | Standard / Bowing | Expression controller mode | ⚙️ Internal setting |

---

## Articulation Recipes from Manual

### Détaché
**Definition:** Separated bow strokes while sustain pedal is pressed

**Requirements:**
- CC64 (Sustain) = 127 (on)
- Note-off of first note BEFORE note-on of second note
- No overlap between notes

**Behavior controlled by NoteOff Sust. parameter:**
- **Hold**: First note sustained
- **Acc.**: Short accent at note end, then fade
- **Fade**: Immediate fade

**Current implementation:** ✅ **IMPLEMENTED (April 2026)**
- Detects "détaché" or "detache" in expression text
- Articulation is handled by slur state management (sustain pedal tracking)
- Notes are processed normally, sustain state managed in main loop
- ⚠️ NoteOff Sust. parameter modes not yet accessible (parameter not discovered)

---

### Martelé
**Definition:** Strong, accented attack with immediate decay

**Recipe:**
1. Set BowLift = "On String"
2. High velocity at note-on (100-127)
3. High expression at note-on (CC11 = 110-127)
4. Decrease expression immediately after attack
5. **For scratchier attack:**
   - Set BowPressure (CC20) to 83-102 (0.65-0.80 normalized) just before attack
   - Quickly decrease to normal (~64) while decreasing expression

**Current implementation:** ✅ **FULLY IMPLEMENTED with bow pressure envelope (April 2026)**
- Expression spike implemented (CC11 peak = 120)
- **Bow pressure envelope: spike to 83-102, decay to 64 after 15 ticks**
- Harmonics boost for attack clarity
- ⚠️ Still missing BowLift parameter (not discovered)

**Envelope pattern:**
```
CC11 (Expression):
120 |▲
    |█▄▄▄▄▄▄▄▄▄▄▄
60  |

CC20 (Bow Pressure) - ✅ NOW IMPLEMENTED:
95  |▲▄▄▄▄▄▄▄▄▄▄  (spike 83-102 then drop to 64)
64  |
```

---

### Spiccato
**Definition:** Bouncing bow, short detached notes

**Recipe:**
1. Set BowLift = "Off String"**Partially implemented (April 2026)**
- Short duration (40%) + expression spike
- Harmonics boost for clarity
- Light bow force (50-75) with variable pressure
- Bow position toward bridge (72) for clarity
- ⚠️ Still missing BowLift parameter control

**Current implementation:** ✅ Implemented as text articulation (short duration + expression spike)

**Required enhancement:** Need to set BowLift parameter

---

### Slurred Legato
**Definition:** Smooth connection on same string

**Recipe:**
1. Overlap second note with first note
2. **High velocity for second note (90-127)** ← Key for legato trigger
3. **CC64 (Sustain) = 127** for smooth connection
4. Second note on **same string** as first note (controlled by Alt.Fing)

**Current implementation:** ✅ **FULLY IMPLEMENTED (April 2026)**
- CC64 activated when entering slur region
- High velocity (90+) for overlapped notes in slur
- 20% note overlap for smooth connection
- Velocity-based differentiation from portamento


---

### Cross-String Legato
**Definition:** Smooth connection across different strings

**Recipe:**
1. Overlap second note with first note
2. High velocity for second note (90-127)
3. Second note on **different string** than first (controlled by Alt.Fing parameter)

**Current implementation:** ⚠️ Not implemented (no Alt.Fing control)

---

### Portamento (Glissando)
**Definition:** Audible pitch slide between notes

**Recipe:**
1. Overlap second note with first note
2. **Low velocity for second note (10-50)** ← Key difference from legato
3. Set CC5 (Portamento Time) to desired slide duration
4. Threshold between legato/portamento controlled by "Port/Leg Speed&Thresh"

**Continuous vs Split Portamento:**
- **Same string**: Continuous slide on one string
- **Different strings**: Split across two strings (split point controlled by Portam. Split Ratio)

**Current implementation:** ✅ **FULLY IMPLEMENTED with velocity differentiation (April 2026)**
- CC5 with interval-aware scaling
- High velocity (90+) triggers legato, low velocity triggers portamento
- Automatic portamento for plain notes (excludes slurred notes)

---

### Flautato ✅ **IMPLEMENTED (April 2026)**
**Definition:** Airy, flute-like tone

**Recipe:**
1. Set BowPressure (CC20) to 15 (very light bow)
2. Add text "flautato" or "flaut." in MuseScore

**Implementation:**
- Detects "flautato" or "flaut." in measure-level text directions
- Persists across all notes until technique is changed
- Sets CC20 = 15 for very light bow pressure
- Produces airy, delicate, flute-like tone
- Implemented in `articulation_detector.py` with stateful technique tracking

---

### Scratch ✅ **IMPLEMENTED (April 2026)**
**Definition:** Very harsh, scratchy tone

**Recipe:**
1. Set BowPressure (CC20) to maximum value (125)
2. Play with high expression for harsh effect
3. Add text "scratch" in MuseScore

**Implementation:**
- Detects "scratch" or "scratchiness" in measure-level text directions
- Persists across all notes until technique is changed
- Sets CC20 = 125 for maximum bow pressure
- Boosts expression by +10 for harsh, gritty, aggressive tone
- Implemented in `articulation_detector.py` with stateful technique tracking
- Note: "Scratch" text appears on SWAM GUI near bow pressure slider

---

### Tremolo

**Auto-Tremolo (SWAM internal):**
- Set tremolo mode to Slow/Fast
- If Sync mode, synchronized to DAW tempo
- Expression "spikes" can accent specific strokes

**Manual Tremolo:**
1. Set "Manual Trem/BowC KS" to "Trem"
2. Press/release KeySwitch C# while playing
3. Bow change occurs at both note-on and note-off
4. Adjust BowPressure for smooth/hard effect

**Bowing Mode:**
1. Set Gesture Mode to "Bowing"
2. Move expression controller back/forth for bow changes

**Current implementation:** ✅ Auto-tremolo via CC60 (continuous speed control)

---

### Crescendo Effects

**Standard Crescendo:**
- Increase CC11 (Expression) from low to high

**Wider Crescendo:**
- Map BowPressure to **same CC as Expression**
- Example mapping:
  - Expression: CC11 → range 0-127
  - BowPressure: CC11 → range 55-80
- Both parameters increase together for wider dynamic range

**Fade-in from Nothing:**
1. Set Expression (CC11) to 0
2. Hit key with very low velocity (<10)
3. Gradually increase Expression

**Current implementation:** ✅ Crescendo via CC11, ⚠️ Coupled bow pressure not implemented

---

## Special Techniques

### Same-String Portamento
**Challenge:** Avoiding split portamento across strings

**Solution using Alt.Fing:**
1. Set Alt.Fing to "Nut+Open" (high value) BEFORE first note
2. Press first note (e.g., E3 on D string, near scroll)
3. Set Alt.Fing to "Bridge" (mid value) BEFORE second note
4. Press second note (e.g., E4 on same D string, near bridge)
5. Continuous portamento occurs on one string

**Current implementation:** ❌ Not implemented (no Alt.Fing control)

---

## Implementation Priority

### High Priority (Common Articulations)
1. ✅ **Staccato** - Implemented
2. ✅ **Accent** - Implemented
3. ✅ **Legato** - Implemented (CC64 + high velocity + overlap)
4. ✅ **Slur** - Implemented (CC64 + high velocity + 20% overlap)
5. ✅ **Portamento** - Implemented with velocity differentiation
6. ✅ **Tremolo** - Implemented
7. ✅ **Pizzicato** - Implemented (CC61=50, April 2026)
8. ✅ **Martelé** - Implemented with bow pressure envelope (CC20 spike 83-102 → 64)
9. ⚠️ **Spiccato** - Partially implemented (needs BowLift parameter)
10. ✅ **Détaché** - Implemented (CC64=127, separated notes)

### Medium Priority (Color Effects)
1. ✅ **Col Legno** - Implemented (CC61=90, April 2026)
2. ✅ **Flautato** - Implemented (CC20=15, April 2026)
3. ✅ **Scratch** - Implemented (CC20=125, April 2026)
4. ✅ **Sul Ponticello** - Implemented (CC21=115)
5. ✅ **Sul Tasto** - Implemented (CC21=15)

### Low Priority (Advanced Control)
1. ❌ **Alt.Fing** - String selection (complex, may not be needed for basic MIDI)
2. ❌ **Port/Leg Speed&Thresh** - Fine-tuning threshold
3. ❌ **Dynamic Transit.** - Legato quality tuning
4. ❌ **Cross-String Legato** - Requires Alt.Fing
5. ❌ **Manual Tremolo** - KeySwitch based, not suitable for automated processing

---

## BowPressure (CC20) Value Guide

Based on manual and testing:

| CC20 Value | Normalized | Effect | Sound Character |
|------------|------------|--------|-----------------|
| 0-20 | 0.00-0.16 | **Flautato** | Very airy, weak, flute-like |
| 21-50 | 0.16-0.39 | Light | Soft, delicate, sul tasto-like |
| 51-64 | 0.40-0.50 | Normal-Light | Standard playing, slightly under |
| 65-75 | 0.51-0.59 | Normal | Natural, balanced tone |
| 76-82 | 0.60-0.65 | Firm | Rich, full tone |
| 83-102 | 0.65-0.80 | **Martelé Range** | Pressed, strong, articulated |
| 103-119 | 0.81-0.94 | Very Heavy | Dense, forced tone |
| 120-127 | 0.94-1.00 | **Scratch** | Harsh, gritty, aggressive |

**Current implementation:** CC20 used with basic coupling to CC11, not fully exploiting these ranges

---

## Next Steps

1. **Discover missing CC mappings:**
   - Use Ableton envelope testing (see [ableton_envelope_guide.md](ableton_envelope_guide.md))
   - Document exact thresholds for BowLift, Bow Mode, NoteOff Sust., etc.

2. **Implement BowPressure envelopes:**
   - Add flautato articulation (CC20 = 15)
   - Add scratch technique support
   - Dynamic bow pressure for martelé (spike then decay)

3. **Enhance existing articulations:**
   - Martelé: Add bow pressure envelope (83-102 → 64)
   - Spiccato: Add BowLift control when discovered
   - Crescendo: Implement coupled bow pressure option

4. **Add to MusicXML detection:**
   - Recognize "flautato" text → set CC20 low
   - Recognize "martelé" text → set expression + bow pressure spikes
   - Recognize "scratch" text → set CC20 high

5. **Test and validate:**
   - Create test MIDI files with each articulation
   - Compare with real violin recordings
   - Iterate on CC values for musicality

---

## Version Notes

**SWAM Version Tested:** Solo Strings v2.0 (manual rev. 3)

**Note:** Parameter mappings and thresholds may vary between SWAM versions. Always test with your specific SWAM version and document results.
