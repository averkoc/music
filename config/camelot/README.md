# Camelot MIDI Mapping Integration

**Camelot** is made by **Audio Modeling** - the same company that creates SWAM instruments! This means Camelot has native, optimized MIDI mappings for SWAM instruments built right in.

## What is Camelot?

Camelot (by Audio Modeling) is a MIDI processing and routing tool specifically designed to work with SWAM instruments. It can:
- Route MIDI between applications
- Transform MIDI messages in real-time
- Apply expression curves and CC mappings
- **Includes native SWAM presets out of the box**

Since both products are from Audio Modeling, the integration is seamless and doesn't require manual CC mapping!

## Why Camelot + SWAM Work So Well Together

**Native Integration Benefits:**
- ✅ Pre-configured mappings for all SWAM instruments
- ✅ Optimized CC curves designed by Audio Modeling
- ✅ Real-time processing with minimal latency
- ✅ Regular updates alongside SWAM releases
- ✅ No manual CC configuration needed

## Setup Instructions

### 1. Install Camelot

Download and install Camelot from [Audio Modeling website](https://audiomodeling.com/)

**Note**: Camelot may come bundled with SWAM instruments or available separately.

### 2. Basic Routing Setup

Camelot provides built-in templates for MuseScore → SWAM workflow:

#### In MuseScore:
1. Edit → Preferences → I/O
2. Set MIDI Output to virtual MIDI port or Camelot input

#### In Camelot:
1. Input: MuseScore MIDI output
2. Select SWAM preset (Violin, Saxophone, etc.)
3. Output: Your DAW's MIDI input  
4. Enable SWAM-specific processing

#### In Your DAW:
1. Create MIDI track
2. Set input to Camelot output
3. Load matching SWAM VST3 plugin
4. Arm track for recording

### 3. Using Native SWAM Presets

Camelot includes factory presets for each SWAM instrument:

**For Violin:**
- Natural vibrato mapping
- Bow speed (CC74) control
- Expression curves optimized for strings

**For Saxophone:**
- Breath pressure (CC2) mapping
- Jazz vs. classical presets
- Growl and articulation effects

**Simply select the preset matching your SWAM instrument!**

### 4. Live Processing

Camelot excels at real-time processing:
1. Play from MuseScore
2. Camelot applies SWAM-optimized CC messages automatically
3. SWAM responds with professional, expressive playback
4. Record in DAW if desired

## Camelot vs. Python Scripts

### Use Camelot When:
- ✅ You want real-time playback from MuseScore
- ✅ You prefer native Audio Modeling integration
- ✅ You need minimal setup (just select preset)
- ✅ You want to perform live with MIDI controller

### Use Python Scripts When:
- ✅ You want offline/batch processing
- ✅ You need custom CC mapping logic
- ✅ You want to modify articulation algorithms
- ✅ You prefer MusicXML parsing over MIDI
- ✅ You want version control for processing settings

**Best of both**: Use Camelot for quick tests and live performance, Python scripts for refined production work!

## Integration with MusicXML Python Scripts

**Powerful workflow combination:**

1. **Export from MuseScore**: MusicXML file
2. **Process with Python script**: Extract articulations, generate base MIDI
3. **Route through Camelot**: Apply Audio Modeling's native CC curves
4. **Record in DAW**: Final expressive MIDI

This gives you:
- Articulation preservation from MusicXML
- Custom processing logic from Python
- Professional CC curves from Camelot
- Best of all worlds!

## Troubleshooting

### Camelot Not Showing SWAM Presets
- Ensure Camelot and SWAM are both installed
- Check for Camelot updates from Audio Modeling
- SWAM presets should appear automatically

### No Sound from SWAM
- Check MIDI routing in DAW
- Ensure Camelot output is connected
- Verify SWAM plugin is on correct channel

### Latency Issues
- Reduce buffer size in DAW
- Use ASIO drivers (Windows) or Core Audio (Mac)
- Camelot is optimized for low latency with SWAM

## Alternative: Python-Only Workflow

If you prefer offline processing without Camelot, use the Python scripts:
- `process_musicxml.py` - Full MusicXML parsing (recommended)
- `process_midi.py` - Basic MIDI enhancement

## Resources

- [Audio Modeling Website](https://audiomodeling.com/) - Download Camelot & SWAM
- [SWAM Documentation](https://audiomodeling.com/documentation) - MIDI implementation
- [Camelot User Guide](https://audiomodeling.com/camelot) - Official manual

## Important Note

**This documentation previously referred to "CameloPro" by "Camel Audio" - that was incorrect.** 

The correct product is **Camelot by Audio Modeling**, which is specifically designed for SWAM instruments. Since both are from the same company, the integration is native and you don't need manual CC configuration!
