# CameloPro MIDI Mapping Configuration

CameloPro can automatically route and transform MIDI messages from MuseScore to SWAM instruments.

## What is CameloPro?

CameloPro (formerly Camel Phat Pro) is a MIDI processing tool that can:
- Map MIDI CC messages
- Transform velocity to CC values
- Add expression curves
- Route between virtual MIDI ports

## Setup Instructions

### 1. Install CameloPro

Download and install CameloPro from [Camel Audio website](https://www.camelaudio.com/)

### 2. Import SWAM Presets

CameloPro presets for SWAM instruments are included in this folder:
- `camelopro_swam_violin.xml` - Violin CC mappings
- `camelopro_swam_saxophone.xml` - Saxophone CC mappings

To import in CameloPro:
1. Open CameloPro
2. File → Import Preset
3. Select the appropriate XML file

### 3. Configure MIDI Routing

#### In MuseScore:
1. Edit → Preferences → I/O
2. Set MIDI Output to "CameloPro In"

#### In CameloPro:
1. Input: MuseScore (or virtual MIDI port)
2. Output: Your DAW's MIDI input
3. Enable preset for your target instrument

#### In Your DAW:
1. Create MIDI track
2. Set input to "CameloPro Out"
3. Load SWAM Violin or Saxophone VST3
4. Arm track for recording

### 4. Live Processing

CameloPro can process MIDI in real-time:
1. Play from MuseScore
2. CameloPro adds CC messages on-the-fly
3. SWAM responds with expressive playback
4. Record in DAW if desired

## Preset Details

### Violin Preset Features
- Velocity → CC11 (Expression) with exponential curve
- Automatic CC1 (Vibrato) on sustained notes
- CC74 (Brightness) mapped to note velocity
- Legato detection (overlapping notes → CC64 on)

### Saxophone Preset Features
- Velocity → CC2 (Breath) with custom curve
- Velocity → CC11 (Expression) secondary mapping
- CC1 (Vibrato) on long notes with delay
- Staccato detection → reduced breath pressure

## Advanced Configuration

### Custom CC Mappings

CameloPro allows you to create custom mappings:

1. **Velocity Curves**: Adjust how note velocity affects CC values
2. **Time-based CC**: Add gradual CC changes over note duration
3. **Conditional Processing**: Apply different rules based on note range or velocity
4. **Multi-CC**: Map single input to multiple output CCs

### Expression Curves

For natural-sounding dynamics:
- **Crescendo**: Gradual CC11 increase over time
- **Diminuendo**: Gradual CC11 decrease
- **Natural decay**: Slight CC11 reduction on long notes
- **Attack boost**: Brief CC11 spike at note start

## Troubleshooting

### No Sound from SWAM
- Check MIDI routing in DAW
- Ensure CameloPro output is connected
- Verify SWAM channel matches MIDI channel

### CC Messages Not Working
- Open MIDI monitor to verify CC messages
- Check SWAM parameter assignments
- Confirm CC numbers match SWAM expectations

### Latency Issues
- Reduce buffer size in DAW
- Use ASIO drivers (Windows) or Core Audio (Mac)
- Disable unnecessary CameloPro processing

## Alternative: Python Scripts

If you prefer offline processing over real-time routing, use the Python scripts in the `scripts/` folder instead of CameloPro.

## Resources

- [CameloPro Manual](https://www.camelaudio.com/docs)
- [SWAM MIDI Implementation](https://audiomodeling.com/documentation)
- [Virtual MIDI Ports](https://www.tobias-erichsen.de/software/loopmidi.html) (Windows)
