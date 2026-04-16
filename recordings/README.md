# MIDI Output Recordings

This directory stores recorded MIDI output captures for comparison analysis.

## File Naming Convention

Use descriptive names that indicate:
- Source (ableton/webpage)
- File being played
- Tempo setting (if modified)

Examples:
- `ableton_pala1_100pct.json` - Ableton playing pala1 at 100% tempo
- `webpage_pala1_100pct.json` - Web player playing pala1 at 100% tempo
- `webpage_dpriver_150pct.json` - Web player at 150% tempo

## Creating Recordings

See [docs/output_comparison_guide.md](../docs/output_comparison_guide.md) for full instructions.

Quick commands:
```bash
# Record Ableton output
python scripts/record_midi_output.py --record recordings/ableton_test.json --duration 60

# Record webpage output
python scripts/record_midi_output.py --record recordings/webpage_test.json --duration 60

# Compare
python scripts/record_midi_output.py --compare recordings/ableton_test.json recordings/webpage_test.json
```

## What Gets Recorded

Each JSON file contains:
- Precise timestamps (microsecond accuracy)
- All MIDI messages (Note On/Off, CC, etc.)
- Message metadata (note numbers, velocities, CC values)
- Recording duration and start time

This allows programmatic verification of timing accuracy between different playback methods.
