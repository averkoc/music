# Articulation Mapping Guide

This guide explains how musical articulations from MuseScore are mapped to SWAM instrument CC messages for realistic, expressive playback.

## Overview

SWAM instruments are **physically modeled** virtual instruments that respond to continuous MIDI CC (Control Change) messages to create realistic performances. Unlike sample-based instruments, SWAM requires careful articulation and expression control for natural sound.

## Key MIDI CC Numbers for SWAM

**Note**: These CC mappings are verified against SWAM's official MIDI mapping export from Audio Modeling (see [EXPORTED_MIDIMAPPING.swam](EXPORTED_MIDIMAPPING.swam) for the actual SWAM preset file).

| CC# | Name | Purpose | Typical Range |
|-----|------|---------|---------------|
| **CC1** | Modulation | Vibrato depth/speed | 0 (none) to 127 (intense) |
| **CC2** | Breath | Air pressure (winds) | 40-100 (normal playing) |
| **CC5** | Portamento | Pitch slide time | 1 (min) to 127 (slow glide) |
| **CC17** | Vibrato Rate | Vibrato speed | 0 to 127 |
| **CC20** | Bow Force | Bow pressure | 0 to 127 |
| **CC21** | Bow Position | Sul pont ↔ Sul tasto | 0 (tasto) to 127 (ponte) |
| **CC11** | Expression | Dynamic level | 20 (ppp) to 127 (fff) |
| **CC18** | Growl | Harmonic distortion (sax) | 0 (clean) to 100 (growling) |
| **CC64** | Sustain | Legato mode | 0 (off) or 127 (on) |
| **CC68** | Legato Switch | Legato articulation | 0-127 (some instruments) |
| **CC74** | Brightness | Tone color | 0 (dark) to 127 (bright) |

## Articulation Mappings

### 1. Crescendo (<)

**Musical Symbol**: Hairpin opening to the right  
**Effect**: Gradual increase in volume/intensity

**MIDI Implementation**:
```json
{
  "cc": 11,
  "ramp_type": "exponential",
  "steps": 15
}
```

**Reasoning**:
- **Exponential vs Linear**: Human perception of loudness is logarithmic, so an exponential CC11 ramp sounds more natural than linear
- **Number of steps**: 15 steps provides smooth ramps without excessive MIDI data
- Uses **CC11** (Expression) rather than velocity because SWAM responds better to continuous control

**Usage**:
```python
messages = mapper.create_exponential_crescendo(
    start_value=50,  # p (piano)
    end_value=95,    # f (forte)
    duration_ticks=1920,  # 4 beats at 480 ticks/beat
    steps=15,
    curve=2.0  # Exponential curve factor
)
```

---

### 2. Slur / Legato

**Musical Symbol**: Curved line connecting notes  
**Effect**: Smooth, connected notes without re-articulation

**MIDI Implementation**:
```json
{
  "cc64": 127,
  "cc5_portamento": 40,
  "note_overlap": true,
  "overlap_percent": 15
}
```

**Reasoning**:
- **CC64 (Sustain)**: Enables legato mode in SWAM, telling the instrument not to re-tongue/re-bow
- **CC5 (Portamento)**: Adds subtle pitch slide between notes for realistic legato
- **Note Overlap**: Notes must overlap slightly (10-15%) for smooth transitions
- **Higher portamento for slurs**: Slurs have more noticeable glide than simple legato

**Key Distinction**:
- **Legato**: Smooth connection, minimal portamento (CC5 = 20-30)
- **Slur**: More pronounced slide, higher portamento (CC5 = 40-50)

---

### 4. Glissando

**Musical Symbol**: Glissando line between notes  
**Effect**: Continuous pitch slide from one note to another

**MIDI Implementation**:
```json
{
  "cc5_portamento": 110,
  "cc64": 127,
  "note_overlap": true,
  "overlap_percent": 50
}
```

**Reasoning**:
- **CC5 (Portamento)**: Very high value (110) for dramatic, obvious pitch slide
- **CC64 (Sustain)**: Enables legato mode for continuous sound
- **Note Overlap**: **CRITICAL** - The glissando note MUST overlap with the next note for SWAM to produce the pitch glide
- **50% Overlap**: Long overlap ensures the slide is clearly audible and smooth
- **How SWAM Glissando Works**: The pitch glide occurs when two notes overlap while CC5 is active - the first note slides into the second

**Key Distinction from Slur**:
- **Slur**: Subtle slide, shorter overlap (10-15%), moderate portamento (CC5 = 40)
- **Glissando**: Dramatic slide, longer overlap (50%), very high portamento (CC5 = 110)

**Implementation Note**: After the glissando note ends, CC5 is reset to 0 to prevent affecting subsequent notes.

---

### 5. Vibrato Mark

**Musical Symbol**: Wavy line above notes (~~~~)  
**Effect**: Pitch oscillation that develops after note onset

**MIDI Implementation**:
```json
{
  "cc1_target": 64,
  "delay_ms": 500,
  "ramp_duration_ms": 300
}
```

**Reasoning**:
- **Delayed onset**: Real performers don't apply vibrato immediately; 500ms delay sounds natural
- **Gradual ramp**: CC1 increases smoothly over 300ms to avoid sudden "wobble"
- **Moderate depth**: CC1 = 64 is good default (adjust 40-80 for taste)
- **Not instant**: Avoids unnatural "turning on" of vibrato

**Calculation**:
```
Delay in ticks = (delay_ms / ms_per_beat) × ticks_per_beat
At 120 BPM: (500ms / 500ms) × 480 = 480 ticks (1 beat)
```

---

### 6. Staccato (.)

**Musical Symbol**: Dot above note  
**Effect**: Short, detached note with emphasized attack

**MIDI Implementation**:
```json
{
  "note_duration_percent": 50,
  "cc11_spike": 105,
  "cc11_base_offset": 0
}
```

**Reasoning**:
- **Spike-and-drop**: CC11 jumps to 105, then drops to 0 after 5-10 ticks
- **50-60% duration**: Written quarter note plays as about eighth note length
- **Don't use velocity alone**: SWAM needs CC11 movement for accent
- **Immediate drop**: Creates the "detached" character

**Timing**:
```
t=0: Note ON + CC11=105 (spike)
t=5: CC11=0 (drop immediately)
t=240 (50%): Note OFF (if original was 480 ticks)
```

**Typical durations**:
- Staccato: 50-60% of written value
- Staccatissimo: 25-30% of written value
- Spiccato (strings): 40-45% of written value

---

### 5. Sul Ponticello

**Musical Symbol**: "sul pont." text or technique marking  
**Effect**: Bow very close to bridge → bright, glassy, metallic tone

**MIDI Implementation**:
```json
{
  "cc21_value": 115,
  "cc21_range": [110, 127]
}
```

**Reasoning**:
- **CC21**: Controls bow position on string instruments
- **High values (110-127)**: Near bridge = bright, thin tone
- **Configurable range**: Subtle sul pont (110) to extreme (127)
- **Only for strings**: Not applicable to saxophone

**Opposite Technique**:
```json
"sul_tasto": {
  "cc9_value": 15,
  "cc9_range": [0, 20]
}
```
Low CC9 values = bow over fingerboard = soft, dark, flute-like tone

---

### 6. Accent (>)

**Musical Symbol**: > above note  
**Effect**: Emphasized attack without shortening note duration

**MIDI Implementation**:
```json
{
  "cc11_peak": 110,
  "velocity_boost": 20
}
```

**Reasoning**:
- **Brief spike**: CC11 jumps to 110, then returns to base dynamic after ~10 ticks
- **Full duration**: Unlike staccato, note plays for full written length
- **Velocity boost**: Optional reinforcement of attack
- **Returns to base**: Doesn't affect overall phrase dynamics

**Differs from Staccato**:
| Feature | Staccato | Accent |
|---------|----------|--------|
| Duration | Shortened (50%) | Full length |
| CC11 behavior | Spike → 0 → restore | Spike → return to base |
| Character | Detached | Emphasized |

---

## Instrument-Specific Differences

### Violin vs Saxophone

#### Violin Configuration
```json
{
  "staccato": {
    "note_duration_percent": 50,
    "cc11_spike": 105
  },
  "legato": {
    "cc64": 127,
    "overlap_percent": 10
  }
}
```

#### Saxophone Configuration
```json
{
  "staccato": {
    "note_duration_percent": 55,
    "cc2_spike": 100,
    "cc11_spike": 100
  },
  "legato": {
    "cc64": 127,
    "cc2_constant": 80,
    "overlap_percent": 10
  }
}
```

**Key Differences**:
- **Saxophone uses CC2 (Breath)**: Essential for wind instruments
- **Slightly longer staccato**: 55% vs 50% (harder to play ultra-short on winds)
- **Different CCs for accent**: Breath + Expression for sax vs just Expression for violin
- **Additional articulations**: Saxophone has `slap_tongue` and `growl`

---

## Advanced Techniques

### Exponential vs Linear Ramps

**Linear Crescendo**:
```
CC11 values: 50, 55, 60, 65, 70, 75, 80, 85, 90, 95
Even steps of 5
```

**Exponential Crescendo**:
```
CC11 values: 50, 52, 55, 59, 64, 70, 77, 85, 93, 95
Accelerating curve
```

**Why exponential sounds better**:
- Matches human perception (logarithmic loudness)
- More dramatic crescendo effect
- Avoids "sudden jump" at the end

**Implementation**:
```python
for i in range(steps):
    normalized = i / steps
    curved = normalized ** 2.0  # Exponential curve
    value = start + (range × curved)
```

### Note Overlap for Legato

**Why overlap is necessary**:
```
Without overlap:
Note 1: [========]     60  (gap)
Note 2:              [========]  62

With 10% overlap:
Note 1: [=========]     60
Note 2:         [========]  62
           ^^^^ overlap region
```

The overlap ensures no silence between notes, critical for legato.

**Recommended percentages**:
- Simple legato: 5-10%
- Slur/portamento: 10-15%
- Heavy legato: 15-20%

### Timing Conversions

**MIDI ticks to milliseconds**:
```python
# Given: tempo_bpm = 120, ticks_per_beat = 480
ms_per_beat = 60000 / tempo_bpm  # 500ms at 120 BPM
ms_per_tick = ms_per_beat / ticks_per_beat  # 1.04ms per tick

# Convert 500ms delay to ticks:
delay_ticks = (500 / ms_per_beat) × ticks_per_beat
            = (500 / 500) × 480 = 480 ticks
```

---

## Customization Guide

### Editing `swam_config.json`

1. **Find your instrument section** (violin or saxophone)
2. **Locate the articulation** you want to modify
3. **Adjust parameters** within reasonable ranges
4. **Test and refine**

**Example: Making staccato shorter**
```json
"staccato": {
  "note_duration_percent": 40,  // Changed from 50
  "cc11_spike": 110,             // Changed from 105 (more accent)
  "description": "Very short staccato"
}
```

### Safe Ranges

| Parameter | Safe Range | Default | Notes |
|-----------|------------|---------|-------|
| `cc11_spike` | 95-115 | 105 | Too high (>120) sounds harsh |
| `note_duration_percent` | 25-70 | 50 | Below 25 = barely audible |
| `cc1_target` | 40-80 | 64 | Below 40 = subtle, above 80 = exaggerated |
| `delay_ms` | 200-800 | 500 | Below 200 = too fast, above 800 = obvious |
| `overlap_percent` | 5-20 | 10 | Below 5 = gaps, above 20 = muddy |
| `cc21_value` (sul pont) | 105-127 | 115 | Below 105 = less effect |
| `portamento` (CC5) | 20-60 | 40 | Above 60 = exaggerated slide |

---

## Best Practices

### 1. **Use Exponential Ramps for Dynamics**
Sounds more natural than linear.

### 2. **Don't Over-Spike CC11**
Values above 115 can sound harsh. Be conservative.

### 3. **Vibrato Delay is Critical**
Instant vibrato sounds synthetic. Always delay 300-500ms.

### 4. **Test with Real Music**
Synthetic test patterns don't reveal phrasing issues. Use actual scores.

### 5. **Adjust Per Tempo**
Fast tempos need shorter articulations; slow tempos need longer.

### 6. **Combine Articulations Carefully**
Some combinations don't make sense (staccato + legato). The system should prioritize.

### 7. **Instrument-Specific Tuning**
Violin and saxophone have different physical constraints. Don't copy settings blindly.

---

## Troubleshooting

### Problem: Staccato notes inaudible
**Solution**: Increase `note_duration_percent` to 55-60%

### Problem: Crescendo sounds stepped/blocky
**Solution**: Increase `steps` from 15 to 20-25

### Problem: Vibrato too obvious/sudden
**Solution**: Increase `delay_ms` to 600-700 and `ramp_duration_ms` to 400-500

### Problem: Legato sounds choppy
**Solution**: Increase `overlap_percent` to 12-15%

### Problem: Sul ponticello not bright enough
**Solution**: Increase `cc21_value` to 120-125 and adjust `cc74` (brightness)

### Problem: SWAM not responding to articulations
**Solution**: Check that initialization messages are sent (CC11 movement at track start)

---

## References

- [SWAM Documentation](https://www.audiomodeling.com)
- [SWAM MIDI Mapping Preset](EXPORTED_MIDIMAPPING.swam) - Official CC mappings from SWAM
- [MuseScore Articulation Reference](https://musescore.org/en/handbook)
- [MIDI CC Reference](https://www.midi.org/specifications)

---

## Example Workflow

1. **Compose in MuseScore** with articulations
2. **Export as MusicXML**
3. **Process with `process_musicxml.py`**:
   ```bash
   python process_musicxml.py melody.musicxml --instrument violin
   ```
4. **Load in DAW** with SWAM instrument
5. **Adjust config** if needed and re-process
6. **Enjoy expressive playback!**

The configuration-driven approach means you can tweak articulation behavior without changing code—just edit JSON and reprocess.
