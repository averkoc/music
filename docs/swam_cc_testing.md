# SWAM CC Response Testing Guide

## Problem: CC messages not affecting SWAM sound

If manually changing CC1/CC64/CC74 in Ableton doesn't change the SWAM sound, we need to verify which CCs SWAM actually responds to.

## Quick Test in Ableton

1. **Open your MIDI clip** in Ableton
2. **Draw automation** for different CCs one at a time
3. **Play and listen** for any change

### Test CC11 (Expression) - MOST IMPORTANT
This should DEFINITELY work on all SWAM instruments.

1. In envelope view, select **CC11 (Expression)**
2. Draw a ramp from 20 to 127 over a few notes
3. **Expected**: Volume/dynamics should increase dramatically
4. **If no change**: Something is wrong with SWAM setup

### Test CC1 (Modulation/Vibrato)
1. In envelope view, select **CC1 (Modulation)**
2. Draw value at 0, then 64, then 127
3. **Expected**: Vibrato should increase
4. **If no change**: SWAM might use different CC for vibrato

### Test CC74 (Brightness)
1. In envelope view, select **CC74 (Filter Cutoff)**
2. Draw value at 20, then 127
3. **Expected**: Tone should get brighter/harsher
4. **If no change**: SWAM might not map this CC by default

### Test CC64 (Sustain)
1. Set to 127 (on)
2. **Expected**: Legato/sustained notes
3. **If no change**: May need legato playing mode enabled

## Troubleshooting

### If CC11 doesn't work:
🚨 **SWAM may not be receiving MIDI properly**

Check:
1. Is SWAM on the correct MIDI track?
2. Is the track armed/enabled?
3. Does SWAM show MIDI activity in its UI?
4. Try loading a different SWAM instrument
5. Check SWAM's MIDI input settings

### If only CC11 works:
✅ **SWAM is receiving MIDI, but other CCs may be disabled/different**

Solutions:
1. **Check SWAM's MIDI Learn**: Some SWAM instruments have customizable CC mappings
2. **Enable CCs in SWAM**: Look for "MIDI Controllers" or "Expression" panel
3. **Try alternative CCs**:
   - CC2 (Breath) instead of CC1 for expression
   - CC21 instead of CC74 for brightness
   - CC68 instead of CC64 for legato

### If nothing works:
Check SWAM documentation for your specific instrument version.

## Finding SWAM's Active CCs

### Method 1: SWAM UI inspection
1. Open SWAM plugin interface
2. Look for "MIDI" or "Controllers" section
3. Check which CCs are listed/enabled
4. Take a screenshot and share

### Method 2: Process of elimination
Create a test MIDI file with different CC values:
```
CC1: 0 → 127
CC2: 0 → 127  
CC11: 0 → 127 (this MUST work)
CC21: 0 → 127
CC64: 0 → 127
CC74: 0 → 127
```

Listen to which ones cause audible changes.

## Common SWAM CC Mappings

### SWAM Violin (Standard):
- **CC11**: Expression/Dynamics ✓ (always works)
- **CC1**: Vibrato depth/speed
- **CC2**: Breath (for winds)
- **CC21**: Harmonic content
- **CC64**: Sustain/Legato
- **CC68**: Legato mode (some versions)

### SWAM Saxophone (Standard):  
- **CC11**: Expression ✓
- **CC2**: Breath/Air pressure ✓ (primary)
- **CC1**: Vibrato
- **CC21**: Growl

## What to Report Back

Please test and report:
1. ✅ or ❌ **CC11** changes volume
2. ✅ or ❌ **CC1** changes vibrato
3. ✅ or ❌ **CC74** changes brightness
4. ✅ or ❌ **CC64** creates legato
5. Screenshot of SWAM's MIDI/Controller settings panel (if visible)
6. Which SWAM instrument/version you're using

## Temporary Workaround

If only CC11 works, we can:
1. Map ALL expression to CC11 variations
2. Remove CC1/CC74 from the scripts
3. Use note velocity more heavily
4. Focus on CC11 envelope shaping for articulations

Once you report back what works, I'll update the scripts accordingly.
