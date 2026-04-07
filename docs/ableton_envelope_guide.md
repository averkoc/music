# Ableton MIDI Envelope Visualization Guide

How to view and adjust SWAM CC mappings using Ableton Live's envelope editor.

## Viewing CC Envelopes in Ableton

1. **Load your MIDI file** into a MIDI track with SWAM violin
2. **Double-click the MIDI clip** to open it
3. **Click the "E" button** (Envelopes) in the clip view
4. **Select the envelope to view** from the dropdown:
   - CC11 (Expression) - Main dynamics/articulation
   - CC1 (Modulation) - Vibrato depth
   - CC74 (Filter Cutoff/Brightness) - Tone color
   - CC64 (Sustain Pedal) - Legato/slurs

## What to Look For

### Staccato Notes (Current Settings: 35% duration, 40% sustain)

**In CC11 Envelope:**
```
127 |           
115 | ▲         ▲         ▲         (spike to 115)
    | █         █         █
80  | █ ▬▬▬▬▬▬▬ █ ▬▬▬▬▬▬▬ █         (base level ~80)
40  | █▄▄▄▄▄▄▄  █▄▄▄▄▄▄▄  █         (sustain at 40% = ~32)
    |
0   |___|_____|___|_____|___|_____|
    Note Note Note Note Note Note
    On  Off  On  Off  On  Off

Attack: 3 ticks (very quick spike)
Sustain: 40% of base level
Duration: 35% of note length
```

**What this means:**
- **Quick spike** = sharp attack (3 ticks)
- **Drop to 40%** = maintains presence between notes
- **Short note** = 35% duration creates separation
- **Baseline restored** before next note for smooth flow

### Accent Notes (Current Settings: peak 110)

**In CC11 Envelope:**
```
127 |
110 | ▲▬▬▬▬▬▬▬▬▬▬▬▬       (spike to 110, sustain at base)
    | █
80  | █▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬   (base level)
    |
0   |___________________|
    Note On    Note Off

Attack: 10 ticks (quick peak then sustain)
Sustain: Full base level (note continues)
Duration: Full note length
```

### Marcato Notes (Current Settings: peak 120)

**In CC11 Envelope:**
```
127 |
120 | ▲▬▬▬▬▬▬▬▬▬▬▬▬       (very strong spike to 120)
    | ██
80  | ██▬▬▬▬▬▬▬▬▬▬▬▬▬   (base level)
    |
0   |___________________|
    Note On    Note Off

Attack: 15 ticks (slightly longer than accent)
Sustain: Full base level
Duration: Full note length
```

## Adjusting Config Values Based on Envelope View

### If staccato sounds too detached:
- **Increase `note_duration_percent`**: 35% → 40-45%
- **Increase `cc11_sustain_percent`**: 40% → 50-60%
- Look for: Longer note rectangles, higher sustain line in envelope

### If staccato sounds too connected (not crisp):
- **Decrease `note_duration_percent`**: 35% → 25-30%
- **Decrease `cc11_sustain_percent`**: 40% → 20-30%
- **Increase `cc11_spike`**: 115 → 120
- Look for: Shorter notes, lower sustain line, higher peaks

### If staccato attack is too soft:
- **Increase `cc11_spike`**: 115 → 120-125
- Look for: Higher spike peaks in CC11 envelope

### If staccato attack is too harsh:
- **Decrease `cc11_spike`**: 115 → 105-110
- **Increase `attack_ticks`**: 3 → 5-8
- Look for: Lower peaks, gentler slopes

### If accent/marcato needs more punch:
- **Increase peak values**:
  - Accent: 110 → 115-120
  - Marcato: 120 → 125-127
- **Increase brightness** (CC74) boost
- Look for: Higher CC11 peaks, visible CC74 spikes

### If passages need more vibrato:
- **Adjust auto-vibrato thresholds** in code:
  - Currently: notes ≥ 1 beat get light vibrato
  - Change duration thresholds or CC1 values
- Look for: CC1 ramps in envelope view

## Timing Reference

**MIDI Ticks (at 480 tpqn):**
- 480 ticks = 1 quarter note
- 240 ticks = 1 eighth note
- 120 ticks = 1 sixteenth note
- 60 ticks = 1 thirty-second note

**Current Attack Times:**
- Staccato: 3 ticks (~1/160 note) - very quick
- Accent: 10 ticks (~1/48 note) - quick
- Marcato: 15 ticks (~1/32 note) - slightly longer

## Config File Mapping

| Config Value | What It Controls | Where to See It |
|-------------|------------------|-----------------|
| `note_duration_percent` | How long note sounds (25-50%) | Note length in piano roll |
| `cc11_spike` | Attack intensity (105-127) | Peak height in CC11 envelope |
| `cc11_sustain_percent` | Body level (0-100%) | Plateau level in CC11 |
| `attack_ticks` | Attack speed (3-15) | Slope steepness at note start |
| `cc74_brightness` | Tone brightness boost (+0 to +30) | Spike in CC74 envelope |

## Example Workflow

1. **Process your MusicXML** file with current settings
2. **Load MIDI in Ableton** and view CC11 envelope
3. **Note what looks wrong**:
   - Too many/few peaks?
   - Peaks too high/low?
   - Sustain level between notes?
4. **Edit `config/swam_config.json`** based on observations
5. **Re-process** and compare envelopes
6. **Iterate** until it matches your musical intent

## Quick Reference: Current Settings

```json
"staccato": {
  "note_duration_percent": 35,      // See: Note length
  "cc11_spike": 115,                 // See: CC11 peak height
  "cc11_sustain_percent": 40,        // See: CC11 plateau
  "attack_ticks": 3                  // See: CC11 slope
}

"accent": {
  "cc11_peak": 110,                  // See: CC11 peak height
  "attack_decay_ticks": 10           // See: CC11 attack/decay slope
}

"marcato": {
  "cc11_peak": 120,                  // See: CC11 peak height
  "attack_decay_ticks": 15           // See: CC11 attack/decay slope
}
```

## Tips

- **Zoom in** on individual notes to see attack details
- **Compare** multiple staccato notes to check consistency
- **Use automation view** to draw your ideal curve, then match config to it
- **A/B test** by keeping old MIDI files to compare changes
- **Listen while viewing** envelopes to correlate sound with visuals
