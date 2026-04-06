"""
Example: Batch process multiple MIDI files

This script demonstrates how to process multiple MIDI files at once.
"""

import sys
from pathlib import Path
from process_midi import process_midi_file
from swam_cc_mapper import SWAMInstrument


def batch_process(input_dir: str, output_dir: str, instrument: str):
    """
    Process all MIDI files in a directory.
    
    Args:
        input_dir: Directory containing input MIDI files
        output_dir: Directory for processed output files
        instrument: 'violin' or 'saxophone'
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"Error: Input directory not found: {input_path}")
        sys.exit(1)
    
    # Find all MIDI files
    midi_files = list(input_path.glob("*.mid")) + list(input_path.glob("*.midi"))
    
    if not midi_files:
        print(f"No MIDI files found in {input_path}")
        return
    
    print(f"Found {len(midi_files)} MIDI file(s)")
    
    # Map instrument string to enum
    swam_instrument = (
        SWAMInstrument.VIOLIN if instrument == "violin" 
        else SWAMInstrument.SAXOPHONE
    )
    
    # Process each file
    for i, midi_file in enumerate(midi_files, 1):
        print(f"\n[{i}/{len(midi_files)}] Processing: {midi_file.name}")
        
        output_file = output_path / f"{midi_file.stem}_{instrument}_swam.mid"
        
        try:
            process_midi_file(
                midi_file,
                output_file,
                swam_instrument,
                verbose=False
            )
            print(f"  ✓ Saved to: {output_file}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Batch processing complete!")
    print(f"  Processed: {len(midi_files)} files")
    print(f"  Output directory: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_process.py <input_dir> <instrument>")
        print("Example: python batch_process.py midi_input violin")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    instrument = sys.argv[2].lower()
    
    if instrument not in ["violin", "saxophone"]:
        print("Error: instrument must be 'violin' or 'saxophone'")
        sys.exit(1)
    
    output_dir = "midi_output"
    
    batch_process(input_dir, output_dir, instrument)
