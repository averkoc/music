# MuseScore to SWAM Workflow Project

This project converts MuseScore Studio melodies into MIDI with proper articulations and dynamics for SWAM VST3 instruments (violin and saxophone).

## Project Context
- **Primary Language**: Python
- **Main Purpose**: MIDI processing for expressive virtual instruments
- **Key Technologies**: mido library for MIDI manipulation, music21 for MusicXML parsing

## Coding Guidelines
- Use Python type hints for all function signatures
- Follow PEP 8 style guidelines
- Add docstrings to all functions explaining MIDI CC mappings
- Comment SWAM-specific CC values (e.g., CC1 for modulation, CC11 for expression)
- Keep MIDI processing modular for easy adaptation to other SWAM instruments

## SWAM-Specific Notes
- SWAM instruments are highly expressive and respond to continuous MIDI CC messages
- Key CCs: CC1 (modulation/vibrato), CC2 (breath), CC11 (expression), CC74 (brightness)
- Articulations require specific CC combinations for realistic performance
- Processed MIDI files work directly in any DAW with VST3 support
