# Quick Start Guide

Get up and running with MuseScore to SWAM in 5 minutes!

## Prerequisites Check

- [ ] Python 3.8+ installed
- [ ] MuseScore Studio installed
- [ ] SWAM Violin or Saxophone VST3 plugin
- [ ] A DAW (Reaper, Cubase, etc.)

## 5-Minute Setup

### 1. Install Python Dependencies (1 minute)

```bash
cd C:\github\music
pip install -r requirements.txt
```

### 2. Export MusicXML from MuseScore (1 minute)

**Recommended approach for best results:**

1. Open any MuseScore file
2. File → Export → **MusicXML**
3. Save to `musescore_files/test.musicxml`

### 3. Process the MusicXML (30 seconds)

```bash
python scripts/process_musicxml.py musescore_files/test.musicxml --instrument violin -v
```

### 4. Import to DAW (1 minute)

1. Open your DAW
2. Create a MIDI track
3. Load SWAM Violin VST3
4. Import `midi_output/test_violin_swam.mid`

### 5. Play and Enjoy! (1 minute)

Press play and hear your melody with expression!

## What's Different?

Compare the original export with MusicXML-processed MIDI:

**Direct MIDI Export (old way):**
- Notes with velocity only
- Articulations lost or approximated
- Dynamics flattened to velocity values
- Slurs not detectable

**MusicXML Processed (new way):**
- All articulations preserved (staccato, accent, legato, etc.)
- CC11 (Expression) mapped from true dynamic markings
- CC1 (Vibrato) intelligently applied
- CC64 (Legato) for slurred passages
- Dynamic changes (crescendo/diminuendo) detected
- Articulation-specific CC adjustments

## Next Steps

Once you have the basics working:

1. **Read the full workflow guide**: `docs/workflow_guide.md`
2. **Experiment with settings**: Edit `config/swam_config.json`
3. **Try CameloPro**: See `config/camelopro/README.md` for real-time processing
4. **Create presets**: Save your SWAM settings in `presets/`

## Common First-Time Issues

### "Module 'mido' not found"
```bash
pip install mido python-rtmidi
```

### "No such file or directory"
Make sure you're running commands from the project root directory (C:\github\music).

### "SWAM doesn't respond to CC messages"
Check SWAM's MIDI settings tab - ensure CC1, CC11, and CC74 are enabled.

### "Output sounds the same as input"
Use verbose mode (`-v`) to verify CC messages are being added. Check your DAW's MIDI monitor.

## Getting Help

- Check the main [README.md](../README.md)
- Read detailed [workflow guide](workflow_guide.md)
- Review SWAM documentation
- Open an issue on GitHub

Happy composing! 🎵
