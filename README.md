# MuseScore to SWAM Workflow

Convert MuseScore Studio melodies into expressive performances using SWAM VST3 instruments (violin and saxophone) with proper articulations, dynamics, and continuous controllers.

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
- 🔄 Integration with CameloPro MIDI mapping templates
- 📝 Preserve musical expression (vibrato, crescendo, dynamics, articulations)

## Project Structure

```
├── musescore_files/      # Original MuseScore (.mscz) files
├── midi_input/           # MIDI files exported from MuseScore
├── midi_output/          # Processed MIDI files for SWAM
├── scripts/              # Python MIDI processing tools
├── config/               # SWAM CC mappings and CameloPro configs
├── presets/              # SWAM instrument presets
└── docs/                 # Documentation and guides
```

## Setup

### Prerequisites

- Python 3.8 or higher
- MuseScore Studio (for composition)
- SWAM Violin and/or Saxophone VST3 plugins
- CameloPro (optional, for advanced MIDI routing)
- A DAW that supports VST3 (Reaper, Cubase, etc.)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/musescore-to-swam.git
cd musescore-to-swam
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

### Advanced: Using CameloPro

CameloPro provides pre-configured MIDI CC mappings optimized for SWAM instruments:

1. Import CameloPro preset from `config/camelopro/`
2. Route MuseScore MIDI through CameloPro
3. CameloPro will add appropriate CC messages automatically

## SWAM MIDI CC Mappings

### Essential Controllers

| CC# | Parameter | Description |
|-----|-----------|-------------|
| CC1 | Modulation | Vibrato depth and speed |
| CC2 | Breath | Breath pressure (wind instruments) |
| CC11 | Expression | Overall expression/volume |
| CC74 | Brightness | Tone brightness/timbre |
| CC64 | Sustain | Sustain pedal (legato) |

### Articulation Mappings

- **Staccato**: Short notes, reduced CC11
- **Legato**: CC64 on, smooth CC1 transitions
- **Accent**: Peak CC11 at note start
- **Crescendo/Diminuendo**: Gradual CC11 changes

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
- [CameloPro Documentation](https://www.camelaudio.com/)
- [MIDI CC Reference](https://www.midi.org/specifications)

## Acknowledgments

- Audio Modeling for SWAM instruments
- Camel Audio for CameloPro
- MuseScore community
