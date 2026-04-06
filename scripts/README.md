# Scripts

Python tools for processing MuseScore files for SWAM instruments.

## Available Scripts

### `articulation_mapper.py` ⭐ **NEW**

**Configurable articulation system** that maps musical expressions to SWAM CC messages.

**Features:**
- Load articulation settings from `config/swam_config.json`
- Customize behavior per instrument (violin, saxophone)
- Support for advanced articulations:
  - **Crescendo/Diminuendo** - Exponential or linear CC11 ramps
  - **Vibrato Mark** - Delayed vibrato with gradual onset (CC1)
  - **Staccato** - CC11 spike-and-drop with configurable duration
  - **Slur/Legato** - Note overlap + portamento (CC5) + sustain (CC64)
  - **Sul Ponticello/Tasto** - Bow position control (CC9) for strings
  - **Accent** - Brief CC11 spike without shortening notes
  - **Growl** - Jazz effect for saxophone (CC18)

**Configuration Example:**
```json
{
  "staccato": {
    "note_duration_percent": 50,
    "cc11_spike": 105,
    "description": "Short, detached notes"
  },
  "vibrato_mark": {
    "cc1_target": 64,
    "delay_ms": 500,
    "ramp_duration_ms": 300,
    "description": "Natural delayed vibrato"
  }
}
```

**Usage:**
```python
from articulation_mapper import ArticulationMapper
from swam_cc_mapper import SWAMInstrument
from articulation_detector import ArticulationType

mapper = ArticulationMapper(SWAMInstrument.VIOLIN)
messages = mapper.apply_articulation(
    ArticulationType.STACCATO,
    base_cc11=80,
    note_duration_ticks=480,
    tempo_bpm=120
)
```

See `example_articulations.py` for complete examples.

### `swam_cc_mapper.py`

SWAM CC message generator with new methods:
- `apply_staccato()` - Spike CC11 then drop to 0
- `apply_vibrato_delayed()` - Gradual vibrato onset after delay
- `apply_sul_ponticello()` / `apply_sul_tasto()` - Bow position (CC9)
- `apply_portamento()` - Pitch slide effect (CC5)
- `create_exponential_crescendo()` - More natural dynamic curves
- `apply_growl()` - Saxophone growl effect (CC18)

### `articulation_detector.py`

Extracts articulations from MusicXML with support for:
- Standard articulations (staccato, accent, tenuto, etc.)
- Expression marks (crescendo, diminuendo, vibrato)
- Playing techniques (sul ponticello, sul tasto)
- Dynamic markings and wedges

### `example_articulations.py`

Interactive examples showing:
1. How to apply each articulation type
2. Resulting CC messages with timing
3. How to customize configuration
4. Note duration modifications

Run with:
```bash
python example_articulations.py
```

### `process_musicxml.py` ⭐ **RECOMMENDED**

Process MusicXML files with **full articulation preservation**.

**Why use this?**
- Preserves ALL articulations from MuseScore (staccato, accent, tenuto, etc.)
- Detects dynamics as semantic data (pp, mf, ff), not just velocity
- Captures slurs, phrase markings, and expression text
- Intelligently maps articulations to SWAM CC messages
- Handles crescendo/diminuendo wedges accurately

**Usage:**
```bash
python process_musicxml.py <input_file.musicxml> --instrument <violin|saxophone> [options]
```

**Options:**
- `-i, --instrument`: Target SWAM instrument (required)
- `-o, --output`: Custom output path (optional)
- `-v, --verbose`: Print detailed processing info with articulation counts

**Examples:**
```bash
# Basic usage
python process_musicxml.py ../musescore_files/melody.musicxml --instrument violin

# With verbose output to see detected articulations
python process_musicxml.py ../musescore_files/song.musicxml -i saxophone -v

# Custom output
python process_musicxml.py ../musescore_files/piece.musicxml -i violin -o ../midi_output/custom.mid
```

**Supported Articulations:**
- Staccato (.) - Short notes with reduced CC11
- Staccatissimo (.') - Very short notes
- Accent (>) - Emphasized attack with CC11 boost
- Strong Accent/Marcato (^) - Heavy emphasis
- Tenuto (-) - Full value, slight CC11 increase
- Legato/Slurs - CC64 sustain enabled
- And more...

### `process_midi.py` (Basic fallback)

Main script for processing pre-exported MIDI files.

**Limitations:**
- Articulations must be guessed from note duration and velocity
- Dynamics are lost (only velocity available)
- Slurs not detectable
- Less accurate CC mapping

Use this only if you need to process existing MIDI files or prefer the MIDI workflow.

**Usage:**
```bash
python process_midi.py <input_file> --instrument <violin|saxophone> [options]
```

**Options:**
- `-i, --instrument`: Target SWAM instrument (required)
- `-o, --output`: Custom output path (optional)
- `-v, --verbose`: Print detailed processing info

**Examples:**
```bash
# Basic usage
python process_midi.py ../midi_input/melody.mid --instrument violin

# Custom output
python process_midi.py ../midi_input/song.mid -i saxophone -o ../midi_output/custom_name.mid

# Verbose mode
python process_midi.py ../midi_input/test.mid -i violin -v
```

### `batch_process.py`

Process multiple MIDI files at once.

**Usage:**
```bash
python batch_process.py <input_directory> <instrument>
```

**Examples:**
```bash
# Process all MIDI files in midi_input/
python batch_process.py ../midi_input violin

# Process a specific folder
python batch_process.py ../musescore_files/exported saxophone
```

### `articulation_detector.py`

Core library for extracting articulations from MusicXML (imported by `process_musicxml.py`).

**Key Classes:**
- `ArticulationType`: Enum of supported articulations
- `DynamicLevel`: Dynamic markings (ppp → ffff) with CC values
- `NoteArticulation`: Data structure for note expressiondata
- `MusicXMLArticulationDetector`: Main analyzer

**Example usage:**
```python
from music21 import converter
from articulation_detector import MusicXMLArticulationDetector

# Load MusicXML
score = converter.parse('melody.musicxml')

# Analyze
detector = MusicXMLArticulationDetector()
notes, dynamics = detector.analyze_score(score)

# Access articulation data
for note in notes:
    print(f"Note {note.pitch}: {note.articulations}")
    print(f"  Dynamic: {note.dynamic_level.marking}")
    print(f"  In slur: {note.in_slur}")
```

### `swam_cc_mapper.py`

Core library for MIDI CC mapping (imported by other scripts).

**Key Classes:**
- `SWAMInstrument`: Enum for instrument types
- `SWAMCCMapper`: Maps musical expressions to SWAM CCs

**Example usage in Python:**
```python
from swam_cc_mapper import SWAMCCMapper, SWAMInstrument

# Create mapper for violin
mapper = SWAMCCMapper(SWAMInstrument.VIOLIN)

# Generate expression CC from velocity
cc_messages = mapper.velocity_to_expression(velocity=100, time=0)

# Add vibrato
vibrato_msg = mapper.add_vibrato(depth=64)

# Create crescendo
crescendo = mapper.create_crescendo(
    start_value=50, 
    end_value=100,
    duration_ticks=960,
    steps=10
)
```

## Development

### Adding New Instruments

1. Add instrument to `SWAMInstrument` enum in `swam_cc_mapper.py`
2. Define CC mappings in `../config/swam_config.json`
3. Implement instrument-specific processing in `SWAMCCMapper`
4. Update `process_midi.py` argument parser

### Testing

Create test MIDI files and process with verbose mode:
```bash
python process_midi.py test_input.mid -i violin -v
```

Compare input and output in a MIDI editor or DAW.

### Common MIDI CC Numbers

| CC# | Parameter | Used For |
|-----|-----------|----------|
| 1   | Modulation | Vibrato depth/speed |
| 2   | Breath | Air pressure (wind) |
| 7   | Volume | Channel volume |
| 11  | Expression | Dynamic expression |
| 64  | Sustain | Legato/sustain |
| 74  | Brightness | Timbre/tone color |
| 91  | Reverb | Reverb send |

## Requirements

See `../requirements.txt` for dependencies:
- `mido` - MIDI file parsing and creation
- `python-rtmidi` - Real-time MIDI (optional)
- `numpy` - Numerical operations (optional)

## Troubleshooting

### ImportError: No module named 'mido'
```bash
pip install mido python-rtmidi
```

### Permission denied error
Make sure output directory exists or script has write permissions.

### Processing produces no CC messages
Check that velocity values in input MIDI are not all zero. Use verbose mode to debug.
