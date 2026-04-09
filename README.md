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

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Areas for improvement:
- Additional SWAM instrument support (cello, trumpet, etc.)
- More sophisticated articulation detection
- Real-time MIDI processing
- GUI for configuration

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Resources

- [MuseScore Studio](https://musescore.org/)
- [SWAM Instruments](https://audiomodeling.com/)
- [MIDI CC Reference](https://www.midi.org/specifications)

## Acknowledgments

- Audio Modeling for SWAM instruments
- MuseScore community
