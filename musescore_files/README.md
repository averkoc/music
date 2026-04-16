# MuseScore Files

Place your MuseScore Studio (.mscz) files in this directory.

## 🎯 Comprehensive Test File (April 2026)

**📄 [violin_reference_test_complete.xml](violin_reference_test_complete.xml)**  
**📖 [Complete Guide](violin_reference_test_complete_GUIDE.md)**  
**🎵 [Test Output MIDI](../midi_output/test_complete_violin_swam.mid)**

This is the **official comprehensive test file** demonstrating ALL implemented SWAM techniques with stateful tracking (24 measures):

**Techniques Included:**
- ✅ Bow modes: pizzicato (CC61=50), col legno (CC61=90)
- ✅ Bow pressure: flautato (CC20=15), scratch (CC20=125), martelé
- ✅ Bow position: sul ponticello (CC21=115), sul tasto (CC21=15)
- ✅ Articulations: staccato, tenuto, accent, marcato, tremolo
- ✅ Legato & slurs with CC64 and note overlap
- ✅ Vibrato, glissando, dynamics, crescendo/diminuendo

```bash
python scripts/process_musicxml.py musescore_files/violin_reference_test_complete.xml -i violin
```

---

## 🎯 Legacy Reference Test File

**Use `violin_reference_test.xml` as the canonical test file!**

This comprehensive 14-measure file demonstrates ALL supported SWAM features with clear visual markers. See [violin_reference_test_GUIDE.md](violin_reference_test_GUIDE.md) for complete documentation.

To process it:
```bash
python scripts/process_musicxml.py musescore_files/violin_reference_test.xml
```

---

## Recommended Workflow

**Export as MusicXML for best results!**

### Why MusicXML?
- ✅ Preserves ALL articulations (staccato, accent, slurs, etc.)
- ✅ Keeps dynamic markings as semantic data
- ✅ Exports expression text and phrase markings
- ✅ Enables accurate SWAM CC mapping

### How to Export MusicXML

1. File → Export → **MusicXML**
2. Choose "Compressed MusicXML (.mxl)" or "Uncompressed (.musicxml)"
3. Save with descriptive name (e.g., `violin_melody_01.musicxml`)

## Recommended Practices

- Use descriptive filenames (e.g., `violin_melody_01.musicxml`)
- Include instrument name in filename for multi-instrument projects
- Keep backup versions in a separate directory
- Use MuseScore's built-in articulation and dynamic markings liberally
- Add slurs for legato passages
- Mark crescendo/diminuendo with hairpins

## Articulations That Work Best

In MuseScore, use these articulations for accurate SWAM mapping:
- Staccato (.) - Short, detached notes
- Accent (>) - Emphasized notes
- Marcato (^) - Strong emphasis
- Tenuto (-) - Full value notes
- Slurs/Legato - Smooth, connected phrases

## Export Settings (if using MIDI fallback)

If you must export MIDI instead of MusicXML:
1. File → Export → MIDI
2. Ensure "Export RPNs" is enabled
3. Check "Expand repeats" if you want full playback
4. Velocity settings: Use default or "Offset velocity change" if needed

**Note**: MIDI export loses most articulation data!
