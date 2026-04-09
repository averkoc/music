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
        
        # Add initialization messages to wake up SWAM instrument
        # SWAM needs expression movement stimulus to activate
        init_messages = mapper.create_initialization_messages(time=0)
        new_track.extend(init_messages)
        
        if verbose and i == 0:  # Only print once
            print("  Added SWAM initialization stimulus (CC11 movement)")
            print("  Applying CC11 envelopes to all notes...")
            print("  Using interval-aware portamento...")
        
        # Track note state for envelope and portamento
        current_velocity = 64
        current_time = 0
        prev_pitch = None
        active_notes = {}  # Map of pitch -> (start_time, velocity)
        pending_envelopes = []  # Envelopes to add after we know note duration
        
        # First pass: collect note information
        notes_info = []
        abs_time = 0
        for msg in track:
            if not msg.is_meta:
                abs_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes_info.append({
                        'type': 'note_on',
                        'time': abs_time,
                        'pitch': msg.note,
                        'velocity': msg.velocity,
                        'msg': msg
                    })
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    notes_info.append({
                        'type': 'note_off',
                        'time': abs_time,
                        'pitch': msg.note,
                        'msg': msg
                    })
        
        # Second pass: process notes with full context
        abs_time = 0
        last_output_time = 0
        
        for msg in track:
            if not msg.is_meta:
                abs_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Calculate note duration by finding matching note_off
                    duration_ticks = midi_file.ticks_per_beat  # Default to quarter note
                    for info in notes_info:
                        if info['type'] == 'note_off' and info['pitch'] == msg.note and info['time'] > abs_time:
                            duration_ticks = info['time'] - abs_time
                            break
                    
                    # Add interval-aware portamento before the note
                    if prev_pitch is not None:
                        portamento_msg = mapper.apply_portamento_smart(
                            prev_pitch=prev_pitch,
                            current_pitch=msg.note,
                            base_amount=60,
                            time=msg.time
                        )
                        # Only add if portamento amount > 0
                        if portamento_msg.value > 0:
                            new_track.append(portamento_msg.copy(time=msg.time))
                            # Adjust note time since we added a message before it
                            msg = msg.copy(time=0)
                    
                    # Generate CC11 envelope for this note
                    base_cc11 = mapper._velocity_to_cc(msg.velocity)
                    envelope_messages = mapper.create_note_envelope(
                        envelope_type='default',
                        base_cc11=base_cc11,
                        duration_ticks=duration_ticks,
                        velocity=msg.velocity
                    )
                    
                    # Add envelope messages relative to note onset
                    for env_offset, env_msg in envelope_messages:
                        if env_offset == 0:
                            # First envelope message goes with the note
                            new_track.append(env_msg.copy(time=msg.time if prev_pitch is None else 0))
                        else:
                            # Store for later insertion with proper timing
                            pending_envelopes.append((abs_time + env_offset, env_msg))
                    
                    # Update tracking
                    prev_pitch = msg.note
                    current_velocity = msg.velocity
                
                # Add pending envelope messages that should fire before this message
                pending_envelopes.sort(key=lambda x: x[0])
                while pending_envelopes and pending_envelopes[0][0] <= abs_time:
                    env_time, env_msg = pending_envelopes.pop(0)
                    delta = env_time - last_output_time
                    new_track.append(env_msg.copy(time=delta))
                    last_output_time = env_time
                
                # Copy the original message with adjusted time
                if last_output_time < abs_time:
                    delta = abs_time - last_output_time
                    new_track.append(msg.copy(time=delta))
                    last_output_time = abs_time
                else:
                    new_track.append(msg.copy(time=0))
        
        # Add any remaining envelope messages
        for env_time, env_msg in pending_envelopes:
            delta = env_time - last_output_time
            new_track.append(env_msg._replace(time=delta))
            last_output_time = env_time
        
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
