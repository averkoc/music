# MuseScore to SWAM Workflow Guide

Complete guide for converting MuseScore compositions into expressive SWAM instrument performances.

## Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [MuseScore Composition Tips](#musescore-composition-tips)
3. [Exporting from MuseScore](#exporting-from-musescore)
4. [Processing MIDI Files](#processing-midi-files)
5. [DAW Setup](#daw-setup)
6. [SWAM Configuration](#swam-configuration)
7. [Advanced Techniques](#advanced-techniques)

## Workflow Overview

```
┌─────────────────┐
│   MuseScore     │  Compose melody with articulations
│     Studio      │  and dynamics
└────────┬────────┘
         │ Export MIDI
         ▼
┌─────────────────┐
│   MIDI File     │  Standard MIDI with note data
│   (Basic)       │  and velocity information
└────────┬────────┘
         │ Process
         ▼
┌─────────────────┐
│  Python Script  │  Add SWAM-specific CC messages
│  or Camelot     │  (expression, breath, vibrato)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MIDI File     │  Enhanced MIDI with continuous
│   (Enhanced)    │  controller data
└────────┬────────┘
         │ Import to DAW
         ▼
┌─────────────────┐
│  DAW + SWAM     │  Expressive playback with
│     VST3        │  realistic articulations
└─────────────────┘
```

## MuseScore Composition Tips

### Using Articulations

MuseScore articulations are mapped to SWAM controllers:

| MuseScore | Effect | SWAM Mapping |
|-----------|--------|--------------|
| Staccato (.) | Short notes | Reduced CC11, shortened duration |
| Tenuto (-) | Full value | Standard CC11, full duration |
| Accent (>) | Emphasis | Peak CC11, increased velocity |
| Legato (slur) | Connected | CC64 on, note overlap |
| Marcato (^) | Strong accent | High CC11 + CC74 |

**How to add in MuseScore:**
1. Select note(s)
2. Open Articulations palette (F8)
3. Click desired articulation

### Dynamics

Use standard dynamic markings:

```
ppp → pp → p → mp → mf → f → ff → fff
```

**How to add:**
1. Select measure or note
2. Open Dynamics palette
3. Click dynamic marking

### Crescendo and Diminuendo

Use hairpins for gradual dynamic changes:

1. Select note range
2. Open Dynamics palette
3. Choose crescendo (<) or diminuendo (>)
4. Adjust length by dragging endpoints

These will be converted to smooth CC11 transitions.

### Vibrato

For string instruments:
1. Add "vib." text above passage
2. Use trill (~~~) notation for visual reference
3. Processing script will add CC1 modulation

### Tempo Changes

SWAM instruments respond naturally to tempo:
- Ritardando: Adds time for expression
- Accelerando: Maintains energy
- Fermata: Extends note naturally

## Exporting from MuseScore

### Export Settings

1. **File → Export → MIDI**

2. **Recommended settings:**
   - ☑ Expand repeats
   - ☑ Export RPNs (pitch bend)
   - ☐ Use flattened dynamics (keep unchecked)
   
3. **Advanced (Edit → Preferences → Import/Export → MIDI):**
   - Velocity dynamics: Medium (64-127)
   - Staccato: 50%
   - Tenuto: 100%

### File Naming

Save with descriptive names:
- `violin_meditation_v1.mid`
- `sax_jazz_etude_draft.mid`

## Processing MIDI Files

### Method 1: Python Script

```bash
# Basic usage
python scripts/process_midi.py midi_input/melody.mid --instrument violin

# With custom output path
python scripts/process_midi.py midi_input/melody.mid --instrument saxophone --output custom/output.mid

# Verbose mode (see processing details)
python scripts/process_midi.py midi_input/melody.mid --instrument violin -v
```

### Method 2: Camelot (Native SWAM Integration)

See `config/camelot/README.md` for real-time routing setup. Camelot is made by Audio Modeling (same company as SWAM) and includes native presets.

### What the Processing Does

1. **Velocity → CC11 (Expression)**
   - Maps note velocity to expression controller
   - Applies exponential curve for natural dynamics
   - Maintains minimum threshold for audibility

2. **Articulation Detection**
   - Short notes: Reduces CC11, adds brightness
   - Long notes: Adds vibrato (CC1) after delay
   - Note overlaps: Enables legato (CC64)

3. **Dynamic Curves**
   - Crescendo: Gradual CC11 increase
   - Diminuendo: Gradual CC11 decrease
   - Accents: Brief CC11 peaks

4. **Instrument-Specific**
   - **Violin**: Focuses on CC1 (vibrato), CC74 (bow speed)
   - **Saxophone**: Emphasizes CC2 (breath), CC11 (expression)

## DAW Setup

### Recommended DAWs

- **Reaper**: Excellent MIDI editing, low CPU
- **Cubase**: Advanced expression maps
- **Studio One**: Good MIDI tools
- **Logic Pro**: Built-in MIDI FX (Mac only)

### Basic Setup

1. **Create MIDI track**
   
2. **Import processed MIDI**
   - Drag and drop processed .mid file
   - Or: File → Import → MIDI

3. **Load SWAM VST3**
   - Add instrument plugin to track
   - Choose SWAM Violin or Saxophone

4. **Check MIDI routing**
   - Track input: MIDI file
   - Track output: SWAM instrument
   - MIDI channel: Usually 1 (or match in config)

### Monitoring CC Messages

Most DAWs have MIDI monitors:

- **Reaper**: View → MIDI Event List
- **Cubase**: MIDI → Open MIDI Monitor
- **Studio One**: View → Console → MIDI Monitor

Look for CC messages:
```
CC1  (Modulation)
CC11 (Expression)
CC74 (Brightness)
```

## SWAM Configuration

### Loading Presets

1. Open SWAM plugin interface
2. Load preset from `presets/` folder
3. Or configure manually:

### Manual Configuration

**Essential settings:**
- **MIDI Tab**:
  - Enable CC1, CC11, CC74
  - Set response curves to linear or slight exponential

- **Expression Tab**:
  - Link CC11 to overall volume
  - Enable dynamic range

- **Vibrato Tab** (Violin):
  - Link CC1 to vibrato depth/speed
  - Set natural vibrato amount

- **Breath Tab** (Saxophone):
  - Link CC2 to air pressure
  - Enable breath noise

### Testing

Play a few notes and verify:
- ✓ Dynamics respond (CC11)
- ✓ Vibrato works on long notes (CC1)
- ✓ Breath is audible (CC2, saxophone)
- ✓ Articulations sound correct

## Advanced Techniques

### Layering Multiple Takes

1. Export multiple versions with different processing
2. Import all to DAW
3. Blend for complex expression

### Manual CC Editing

After import, draw CC curves in DAW's MIDI editor:
- Add subtle vibrato variation
- Adjust expression for specific phrases
- Fine-tune breath pressure

### Automation

Automate SWAM plugin parameters for additional control:
- Reverb amount per section
- Air noise level
- Bow position (violin)

### Expression Maps (Cubase)

Create expression maps to:
- Switch articulations via keyswitches
- Control CCs from score notation
- Trigger different SWAM presets

### Real-time Performance

Use MIDI keyboard with:
- Mod wheel → CC1 (vibrato)
- Expression pedal → CC11 (dynamics)
- Breath controller → CC2 (saxophone)

## Troubleshooting

### Sounds Flat/Unexpressive

- Check CC11 is active in SWAM
- Verify CC messages in MIDI file
- Increase dynamic range in MuseScore
- Adjust velocity curve in processing script

### Too Much Vibrato

- Reduce CC1 values in processed MIDI
- Adjust vibrato sensitivity in SWAM
- Edit CC1 curve in DAW

### Latency Issues

- Reduce buffer size in DAW
- Use ASIO drivers (Windows)
- Freeze SWAM track after recording

### Articulations Not Working

- Check note durations were exported correctly
- Verify CC64 for legato passages
- Manually edit in DAW if needed

## Tips for Best Results

1. **Start Simple**: Test with a single melody phrase first
2. **Iterate**: Compare MuseScore playback → processed MIDI → SWAM
3. **A/B Testing**: Process with different settings and compare
4. **Save Presets**: Create SWAM presets for different styles
5. **Documentation**: Keep notes on what works for your compositions

## Next Steps

- Explore additional SWAM instruments (cello, trumpet, flute)
- Create custom CameloPro presets for your style
- Develop processing templates for common genres
- Build a library of reusable MIDI patterns

---

**Questions or issues?** Check the main README.md or open an issue on GitHub.
