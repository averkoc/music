"""
MuseScore to SWAM MIDI Processor

This script processes MIDI files exported from MuseScore Studio and enhances them
with continuous controller (CC) messages optimized for SWAM VST3 instruments.

Usage:
    python process_midi.py input.mid --instrument violin
    python process_midi.py input.mid --instrument saxophone --output custom_name.mid
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import mido

from swam_cc_mapper import SWAMCCMapper, SWAMInstrument


def process_midi_file(
    input_path: Path,
    output_path: Path,
    instrument: SWAMInstrument,
    verbose: bool = False
) -> None:
    """
    Process a MIDI file for SWAM instrument compatibility.
    
    Args:
        input_path: Path to input MIDI file
        output_path: Path to save processed MIDI file
        instrument: SWAM instrument type (violin or saxophone)
        verbose: Print detailed processing information
    """
    if verbose:
        print(f"Loading MIDI file: {input_path}")
    
    try:
        midi_file = mido.MidiFile(input_path)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        sys.exit(1)
    
    # Initialize SWAM CC mapper
    mapper = SWAMCCMapper(instrument)
    
    # Create new MIDI file with same settings
    output_midi = mido.MidiFile(ticks_per_beat=midi_file.ticks_per_beat)
    
    if verbose:
        print(f"Processing {len(midi_file.tracks)} track(s)...")
    
    # Process each track
    for i, track in enumerate(midi_file.tracks):
        new_track = mido.MidiTrack()
        
        # Copy track name and other meta messages
        for msg in track:
            if msg.is_meta:
                new_track.append(msg)
                if msg.type == 'track_name' and verbose:
                    print(f"  Track {i}: {msg.name}")
        
        # Process notes and add CC messages
        current_velocity = 64
        current_time = 0
        
        for msg in track:
            if not msg.is_meta:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Add expression CC based on velocity
                    cc_messages = mapper.velocity_to_expression(
                        msg.velocity, 
                        current_time
                    )
                    new_track.extend(cc_messages)
                    current_velocity = msg.velocity
                
                # Copy the original message
                new_track.append(msg)
        
        output_midi.tracks.append(new_track)
    
    # Save processed MIDI file
    if verbose:
        print(f"Saving processed file: {output_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_midi.save(output_path)
    
    if verbose:
        print("✓ Processing complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Process MuseScore MIDI files for SWAM instruments"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input MIDI file path"
    )
    parser.add_argument(
        "-i", "--instrument",
        type=str,
        choices=["violin", "saxophone"],
        required=True,
        help="SWAM instrument type"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output MIDI file path (default: midi_output/[input]_[instrument]_swam.mid)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed processing information"
    )
    
    args = parser.parse_args()
    
    # Setup paths
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        stem = input_path.stem
        output_path = Path("midi_output") / f"{stem}_{args.instrument}_swam.mid"
    
    # Map instrument string to enum
    instrument = SWAMInstrument.VIOLIN if args.instrument == "violin" else SWAMInstrument.SAXOPHONE
    
    # Process the file
    process_midi_file(input_path, output_path, instrument, args.verbose)
    
    print(f"Processed file saved to: {output_path}")


if __name__ == "__main__":
    main()
