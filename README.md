# MuseScore to SWAM Workflow

Convert MuseScore Studio melodies (single-staff sheet music in MusicXML format) into expressive performances using SWAM VST3 instruments (violin and saxophone) with proper articulations, dynamics, and continuous controllers.

## Overview

This project bridges the gap between MuseScore's notation-based composition and SWAM's expressive, physics-modeled instruments. It processes **MusicXML files** (recommended) or MIDI files from MuseScore and generates sophisticated MIDI with continuous CC messages that SWAM instruments need for realistic, expressive playback.

### Why MusicXML? (Recommended)

**MusicXML preserves ALL your articulations and dynamics!**

- ✅ Articulations (staccato, legato, accent) preserved exactly
- ✅ Dynamics (pp, mf, ff) as semantic data, not just velocity
- ✅ Slurs and phrase markings explicitly available
- ✅ Expression text (dolce, espressivo) captured
- ✅ Crescendo/diminuendo wedges detected accurately

MIDI export loses most of this information, requiring guesswork to reconstruct articulations.

## Features

- 🎵 **Recommended**: Process MuseScore MusicXML exports with full articulation preservation
- 🎵 **Alternative**: Process basic MIDI exports (limited articulation detection)
- 🎻 Optimized presets for SWAM Violin and Saxophone
- 🎚️ Intelligent conversion of articulations to SWAM CC messages
- 🎹 Direct DAW integration - processed MIDI works with any DAW supporting VST3
- 📝 Preserve musical expression (vibrato, crescendo, dynamics, articulations)

## Architecture Overview

### Data Flow & Processing Layers

```
┌─────────────────┐
│  MusicXML       │ ← Primary input: MuseScore score with articulations
│  (Input DSL)    │
└────────┬────────┘
         │
         ├─ Explicit: Notes, articulations, dynamics, slurs, vibrato marks
         ├─ Structural: Beat strength, measure numbers, time signatures
         └─ Spanners: Glissando, crescendo/diminuendo wedges
         
         ↓
         
┌─────────────────────────────────────────────┐
│  articulation_detector.py                   │
│  Extracts & enriches score information      │
└────────┬────────────────────────────────────┘
         │
         ├─ Note properties (pitch, duration, velocity)
         ├─ Articulations (staccato, accent, legato, etc.)
         ├─ Structural context (in_slur, beat_strength)
         └─ Sequential context (note_index, previous pitch)
         
         ↓
         
┌─────────────────────────────────────────────┐
│  swam_config.json                           │ ← Configuration DSL
│  Controls interpretation & CC mappings      │
└────────┬────────────────────────────────────┘
         │
         ├─ Feature toggles (metrical_emphasis, portamento, vibrato)
         ├─ Parameters (emphasis amounts, vibrato depths)
         └─ CC mappings (articulation → CC patterns)
         
         ↓
         
┌─────────────────────────────────────────────┐
│  process_musicxml.py                        │
│  Decision engine with musical inference     │
└────────┬────────────────────────────────────┘
         │
         ├─ Context-aware mapping (slurs, beat positions, intervals)
         ├─ Inference layers (metrical emphasis, portamento, vibrato)
         └─ Physical modeling (bow force/position, breath pressure)
         
         ↓
         
┌─────────────────┐
│  MIDI File      │ ← Output: CC messages optimized for SWAM
│  (SWAM-ready)   │
└─────────────────┘
```

### Structural Context & Membership

The processor is **context-aware** — articulations are mapped differently based on structural membership:

**✓ Phrase Context (Currently Implemented):**
- **Slur membership**: Notes inside slurs get smooth bow connections (note-off velocity 20 vs 64)
- **Beat position**: Downbeats receive automatic metrical emphasis (+5 CC11)
- **Pitch register**: Vibrato adapts to string/register (low notes: wider/slower, high notes: narrower/faster)
- **Interval context**: Portamento amount scales with melodic interval size (half-step vs octave)

**✗ Hierarchical Context (Not Yet Implemented):**
- Measure boundaries for phrase shaping
- Position within slur (first/middle/last note)
- Multi-note coordination (bow direction planning)
- Dynamic wedge membership (is note inside crescendo?)

### Musical Inference & Automatic Features

Beyond explicit score markings, the processor adds musical intelligence:

**Configurable (swam_config.json):**
- Metrical emphasis on strong beats (default: enabled)
- Interval-based portamento (default: enabled)
- Baseline vibrato on sustained notes (default: enabled)
- Pitch-dependent vibrato characteristics (default: enabled)

**Always Active:**
- Natural attack envelopes (soft start → full expression)
- CC2 breath/bow pressure coupling (follows CC11 dynamics)
- Note-off velocity from articulation type (physical modeling)
- Duration adjustments (staccato 35%, glissando extended overlap)

**Estimated (when score incomplete):**
- Hairpin endpoints (±2 dynamic levels if no marking at end)

See [docs/phase1_musicxml_integration.md](docs/phase1_musicxml_integration.md) for complete feature documentation.

### ⚠️ CC Mapping Status

**Important**: CC value mappings are **work in progress** and not yet fully tuned for optimal SWAM response. Some articulations and dynamic nuances may not be as audible in the output MIDI as intended. We're actively refining:

- Attack envelope shapes and timing
- Dynamic range compression/expansion curves
- Vibrato onset delays and depth scaling
- Bow force/position relationships
- Articulation CC value peaks and sustain levels

The architecture and structural context awareness are in place — we're now iteratively tuning the numerical parameters through listening tests with actual SWAM instruments.

**Contributions welcome!** If you're a SWAM user with experience in realistic string/wind techniques, your feedback on CC tuning would be valuable.

## Project Structure

```
├── musescore_files/      # Original MuseScore (.mscz) files
├── midi_input/           # MIDI files exported from MuseScore
├── midi_output/          # Processed MIDI files for SWAM
├── scripts/              # Python MIDI processing tools
├── config/               # SWAM CC mappings and configurations
├── presets/              # SWAM instrument presets
└── docs/                 # Documentation and guides
```

## Setup

### Prerequisites

- Python 3.8 or higher
- MuseScore Studio (for composition)
- SWAM Violin and/or Saxophone VST3 plugins
- A DAW that supports VST3 (Reaper, Cubase, Ableton Live, etc.)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/music.git
cd music
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your SWAM instruments paths in `config/swam_config.json`

## Usage

### Recommended Workflow (MusicXML)

1. **Compose in MuseScore Studio**
   - Write your melody with articulations and dynamics
   - Use standard notation (staccato, legato, crescendo, accents, etc.)

2. **Export MusicXML from MuseScore**
   - File → Export → MusicXML
   - Save to `musescore_files/` folder

3. **Process MusicXML for SWAM**
   ```bash
   python scripts/process_musicxml.py musescore_files/your_file.musicxml --instrument violin -v
   ```

4. **Load in Your DAW**
   - Import processed MIDI from `midi_output/`
   - Load SWAM Violin or Saxophone VST3
   - Apply preset from `presets/` folder if desired
   - Enjoy expressive playback with accurate articulations!

### Alternative Workflow (Basic MIDI)

If you prefer to work with MIDI directly:

```bash
python scripts/process_midi.py midi_input/your_file.mid --instrument violin
```

**Note**: MIDI processing has limited articulation detection. MusicXML is strongly recommended for best results.

## SWAM MIDI CC Mappings

### Essential Controllers

**Note**: These CC mappings are verified against SWAM's official MIDI mapping export (see [docs/EXPORTED_MIDIMAPPING.swam](docs/EXPORTED_MIDIMAPPING.swam)).

| CC# | Parameter | Description |
|-----|-----------|-------------|
| CC1 | Modulation | Vibrato depth (0-110 max) |
| CC2 | Breath | Breath pressure (wind instruments) |
| CC5 | Portamento | Pitch slide time (1-127, min=1) |
| CC17 | Vibrato Rate | Vibrato speed/rate |
| CC20 | Bow Force | Bow pressure on strings |
| CC21 | Bow Position | Sul ponticello ↔ Sul tasto (strings) |
| CC11 | Expression | Overall expression/volume |
| CC18 | Growl | Harmonic distortion (saxophone) |
| CC64 | Sustain | Sustain pedal (legato) |
| CC68 | Legato Switch | Legato articulation mode |
| CC74 | Brightness | Tone brightness/timbre |

### Supported Dynamics

All standard dynamics are recognized from MusicXML and mapped to CC11 (Expression):

| Dynamic | Marking | CC11 Value | Description |
|---------|---------|-----------|-------------|
| **pppp** | 𝆏𝆏𝆏𝆏 | 10 | Pianississississimo (extremely soft) |
| **ppp** | 𝆏𝆏𝆏 | 20 | Pianississimo (very very soft) |
| **pp** | 𝆏𝆏 | 35 | Pianissimo (very soft) |
| **p** | 𝆏 | 50 | Piano (soft) |
| **mp** | 𝆐𝆏 | 65 | Mezzo-piano (moderately soft) |
| **mf** | 𝆐𝆑 | 80 | Mezzo-forte (moderately loud) |
| **f** | 𝆑 | 95 | Forte (loud) |
| **ff** | 𝆑𝆑 | 110 | Fortissimo (very loud) |
| **fff** | 𝆑𝆑𝆑 | 120 | Fortississimo (very very loud) |
| **ffff** | 𝆑𝆑𝆑𝆑 | 127 | Fortissississimo (extremely loud) |

### Supported Articulations

All standard articulations are recognized from MusicXML and converted to appropriate SWAM CC messages:

| Articulation | Symbol | SWAM Implementation | Description |
|--------------|--------|---------------------|-------------|
| **Staccato** | • | CC11 spike + 50% duration | Short, detached notes |
| **Staccatissimo** | ▼ | CC11 spike + 25% duration | Very short, detached notes |
| **Accent** | > | CC11 peak at onset | Emphasized attack |
| **Strong Accent** | ^ | Higher CC11 peak | Very strong emphasis |
| **Marcato** | ^ | CC11 peak + firm attack | Strongly accented and separated |
| **Tenuto** | − | Full duration, sustained CC11 | Hold full value |
| **Legato** | (text) | CC64 on, slight CC5 | Smooth connection |
| **Slur** | ⌢ | CC64 on, CC5=40, note overlap | Connected with pitch slide |
| **Spiccato** | (text) | CC11 spike + 40% duration | Bouncing bow (strings) |
| **Detaché** | (text) | Separate bow, normal CC11 | Detached bow strokes (strings) |
| **Sul Ponticello** | (text) | CC21=115 | Near bridge, bright tone (strings) |
| **Sul Tasto** | (text) | CC21=15 | Over fingerboard, dark tone (strings) |

### Supported Expression Elements

Dynamic and expressive markings that span multiple notes:

| Element | Symbol | SWAM Implementation | Description |
|---------|--------|---------------------|-------------|
| **Crescendo** | < | Exponential CC11 ramp up | Gradual increase in volume |
| **Diminuendo** | > | Exponential CC11 ramp down | Gradual decrease in volume |
| **Vibrato** | ~~~~ | Delayed CC1 ramp (500ms) | Pitch oscillation after onset |
| **Portamento** | (line) | CC5 moderate + overlap | Sliding pitch between notes |
| **Glissando** | (line) | CC5=110 + 50% overlap | Dramatic pitch slide |

**Note**: For detailed technical implementation of each articulation (CC values, timing, curves), see [Articulation Mapping Guide](docs/articulation_mapping_guide.md).

## Quick Start

See [Quick Start Guide](docs/quick_start.md) for a 5-minute setup tutorial.

For detailed workflow information, see [Workflow Guide](docs/workflow_guide.md).

## Contributing

Contributions and suggestions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Areas for development:
- Additional SWAM instrument support (cello, trumpet, etc.)
- More sophisticated articulation detection
- Real-time MIDI processing
- GUI for configuration

## License

Copyright (c) 2026 averkoc. All rights reserved.

See [LICENSE](LICENSE) file for details.

## Resources

- [MuseScore Studio](https://musescore.org/)
- [SWAM Instruments](https://audiomodeling.com/)
- [MIDI Control Change Messages](https://midi.org/midi-1-0-control-change-messages)

## Acknowledgments

- Audio Modeling for SWAM instruments
- MuseScore community
