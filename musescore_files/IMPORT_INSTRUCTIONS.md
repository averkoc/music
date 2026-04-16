# How to Import violin_reference_test.xml into MuseScore Studio

## Quick Steps

1. **Open MuseScore Studio**

2. **Import the XML file:**
   - File → Open
   - Navigate to: `musescore_files\violin_reference_test.xml`
   - Click "Open"

3. **If import succeeds:**
   - File → Save As
   - Save as: `violin_reference_test.mscz`
   - Now you can open the .mscz file normally!

4. **If MuseScore shows errors:**
   - Note the error message
   - Try: File → Import → MusicXML
   - Or manually create the file using the guide below

---

## Alternative: Manual Creation in MuseScore

If the XML import fails, you can build the reference test file manually:

### Step 1: Start with existing violin.mscz
1. Open `violin.mscz` (the 12-measure version)
2. This already has measures 1-12

### Step 2: Add Measure 11 - TREMOLO
After measure 10:
1. Insert → Measures → Insert One Measure (×1)
2. Add text marker above staff: "MARKER 11: TREMOLO" (Ctrl+T)
3. Add dynamic: mp
4. Add four quarter notes: A5, A5, G5, F5
5. Select first A5 → Palette → Tremolo → Three-stroke tremolo
6. Repeat for other notes (select, apply tremolo)

### Step 3: Add Measure 12 - PIZZICATO
1. Insert → Measures → Insert One Measure (×1)
2. Add text marker: "MARKER 12: PIZZICATO"
3. Add text above staff: "pizz." (Ctrl+T)
4. Add four quarter notes: E5, D5, C5, B4
5. Select all four notes → Palette → Articulations → Pizzicato
   (Or right-click first note → Note Properties → check "Pizzicato")

### Step 4: Add Measure 13 - MIXED ARTICULATIONS
1. Insert → Measures → Insert One Measure (×1)
2. Add text marker: "MARKER 13: MIXED ARTICULATIONS"
3. Add text: "arco" (return to bowed)
4. Add dynamic: mf
5. Add notes:
   - C5 quarter with staccato
   - D5 quarter with accent
   - E5, F5, G5, A5 as eighth notes with slur connecting them

### Step 5: Add Measure 14 - FINAL CRESCENDO
1. Insert → Measures → Insert One Measure (×1)
2. Add text marker: "MARKER 14: FINAL CRESCENDO"
3. Add crescendo hairpin (< symbol)
4. Add four quarter notes: D5, E5, F5, G5
5. Add fff dynamic before G5
6. Add fermata to G5 (select note → Palette → Fermata)
7. Add final barline (double bar)

### Step 6: Add Text Markers to Existing Measures
Go back and add markers to measures 1-10:
- M1: "MARKER 1: ACCENTS (pp)"
- M2: "MARKER 2: STACCATO (mf)"
- M3: "MARKER 3: TENUTO + MARCATO"
- M4: "MARKER 4: CRESCENDO"
- M5: "MARKER 5: LEGATO SLUR"
- M6: "MARKER 6: DIMINUENDO"
- M7: "MARKER 7: GLISSANDO"
- M8: "MARKER 8: VIBRATO"
- M9: "MARKER 9: SUL PONTICELLO"
- M10: "MARKER 10: SUL TASTO"

To add markers:
1. Right-click above the staff at start of measure
2. Add → Text → System Text (Ctrl+Shift+T)
3. Type marker name
4. Format: Select text → Inspector → Text → Bold (if desired)

### Step 7: Export
1. File → Save as `violin_reference_test.mscz`
2. File → Export → MusicXML (save as `violin_reference_test.xml`)
3. Process with: `python scripts/process_musicxml.py musescore_files/violin_reference_test.xml -i violin`

---

## Troubleshooting

**Problem:** XML import shows "Invalid MusicXML file"
- **Solution:** Use manual creation method above

**Problem:** Tremolo marking doesn't appear
- **Solution:** Palette → Tremolo → Select note first, then click tremolo type

**Problem:** Text markers don't show during playback
- **Solution:** Use "System Text" (Ctrl+Shift+T) instead of "Staff Text"

**Problem:** Markers show but are hard to read
- **Solution:** Select marker text → Inspector → Increase font size to 14-16pt
