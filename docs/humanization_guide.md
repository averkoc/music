# SWAM Humanization Guide

## Overview

Humanization adds natural performance variations to MIDI for realistic SWAM instrument playback. Unlike sample libraries that only vary volume, SWAM's physical modeling requires variation in **timing**, **attack**, and **expression** to sound human.

## The Problem: "Machine Gun" Effect

Without humanization, every MIDI note has:
- Exact timing on the grid
- Identical velocity (attack strength)
- Perfect note duration
- Constant expression (bow pressure)

This creates an unnatural, robotic sound in SWAM instruments because real musicians have natural imperfections.

## Humanization Parameters

| Parameter | What It Does | Effect on SWAM |
|-----------|-------------|----------------|
| **Timing Jitter** | Shifts notes ±5-12ms off-grid | Prevents "machine gun" rhythm; feels human |
| **Velocity Variation** | Randomizes attack ±4-10% | Varies bow bite/tongue pressure between notes |
| **Duration Variation** | Adjusts note length ±1-3% | Natural bow detachment timing |
| **Expression Flutter** | Varies CC11 ±2-6 | Simulates bow pressure fluctuation |
| **Bow Detach Variation** | Adjusts gaps between notes | Mimics natural bow lift imprecision |

## Usage

### Command Line

```bash
# No humanization (precise, robotic)
python scripts/process_musicxml.py input.mxl --instrument violin --humanize none

# Subtle humanization (conservative, barely noticeable)
python scripts/process_musicxml.py input.mxl --instrument violin --humanize subtle

# Default humanization (natural, recommended)
python scripts/process_musicxml.py input.mxl --instrument violin --humanize default

# Aggressive humanization (obvious variation, expressive)
python scripts/process_musicxml.py input.mxl --instrument violin --humanize aggressive
```

### Humanization Levels

#### None (Precise)
- Perfect grid alignment
- Identical velocities from notation
- **Use for**: Mechanical passages, rhythmically precise music

#### Subtle
```
Timing Jitter: ±5ms
Velocity Variation: ±4%
Duration Variation: ±1.5%
Expression Flutter: ±2
```
- Light variation, barely perceptible
- **Use for**: Classical music requiring precision

#### Default (Recommended)
```
Timing Jitter: ±8ms
Velocity Variation: ±7%
Duration Variation: ±2%
Expression Flutter: ±4
```
- Natural human performance
- **Use for**: Most realistic SWAM playback

#### Aggressive
```
Timing Jitter: ±12ms
Velocity Variation: ±10%
Duration Variation: ±3.5%
Expression Flutter: ±6
```
- Obvious imperfection
- **Use for**: Expressive, emotive performances

## How It Works

### 1. Timing Jitter
Real musicians don't play perfectly on the beat. Notes are shifted slightly:
```
Original: |----C----|----D----|----E----|
Humanized: |---C-----|---D------|--E-----|
```

### 2. Velocity Variation
Two identical notes shouldn't sound identical:
```
Original: Note1(vel=100), Note2(vel=100)
Humanized: Note1(vel=97), Note2(vel=104)
```

### 3. Duration Variation
Bow lift timing varies naturally:
```
Original: [Note1: 480 ticks][Note2: 480 ticks]
Humanized: [Note1: 472 ticks][Note2: 489 ticks]
```

### 4. Expression Flutter
Bow pressure fluctuates subtly:
```
Original: CC11=80 (constant)
Humanized: CC11=78, CC11=82, CC11=79, CC11=81...
```

## Key Insights from Gemini AI

> "In SWAM, timing and expression are more important than velocity. If your Python script can inject slight timing jitter (5-10ms), you'll find the violin suddenly 'breathes' in a way that standard MIDI never does."

### Why SWAM is Different

1. **Physical Modeling vs. Samples**
   - Sample library: Recording of a real player
   - SWAM: Real-time physics simulation of bow on string
   
2. **Attack Matters**
   - Velocity in SWAM controls **bow acceleration**, not just volume
   - Same velocity every time = bow hits string at exact same angle
   
3. **Note Overlap Creates Legato**
   - If Note B starts 1 tick before Note A ends → SWAM performs transition
   - If Note B starts 1 tick after Note A ends → bow "lifts"
   - Humanizing gap timing = natural bow detachment

## Configuration

Humanization settings are defined in `config/swam_config.json`:

```json
{
  "global_settings": {
    "humanization": {
      "default": {
        "timing_jitter_ms": 8.0,
        "velocity_variation_percent": 7.0,
        "duration_variation_percent": 2.0,
        "expression_flutter": 4,
        "bow_detach_variation_ms": 5.0
      }
    }
  }
}
```

You can customize these values or create your own humanization profiles.

## Best Practices

### When to Use Humanization

✅ **Use humanization for:**
- Realistic solo instrument performances
- Expressive melodic lines
- Natural SWAM playback

❌ **Don't use humanization for:**
- Rhythmically complex passages requiring precision
- Ensemble synchronization (humanize each part separately)
- If you plan to add humanization in your DAW later

### Combining with DAW Randomization

You can layer humanization:
1. **Python script**: Adds musical humanization (phrasing, expression)
2. **Ableton/Logic randomizer**: Adds micro-variations (performance jitter)

For best results, use **subtle** or **default** in Python, then add light DAW randomization.

### Reproducibility

Each humanization run is random. For reproducible results, set a seed in code:
```python
from humanizer import HumanizationConfig, SWAMHumanizer

config = HumanizationConfig(seed=12345)  # Same variations every time
humanizer = SWAMHumanizer(config)
```

## Technical Implementation

The humanizer applies variations at different stages:

1. **Note Onset** (`humanize_timing`): Before MIDI generation
2. **Velocity** (`humanize_velocity`): Before note-on message
3. **Duration** (`humanize_duration`): Before note-off calculation
4. **Expression** (`humanize_expression`): When generating CC11 messages

Timing safety ensures notes never go backwards in time, preventing MIDI file errors.

## Comparison Example

Generate all levels for comparison:
```bash
python scripts/process_musicxml.py input.mxl -i violin --humanize none -o none.mid
python scripts/process_musicxml.py input.mxl -i violin --humanize subtle -o subtle.mid
python scripts/process_musicxml.py input.mxl -i violin --humanize default -o default.mid
python scripts/process_musicxml.py input.mxl -i violin --humanize aggressive -o aggressive.mid
```

Load all four into your DAW and compare the feel!

## References

- Gemini AI insights on SWAM physical modeling
- Audio Modeling SWAM documentation
- music21 library for MusicXML parsing
- mido library for MIDI generation
