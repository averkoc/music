"""
MuseScore MusicXML to SWAM MIDI Processor

This script processes MusicXML files exported from MuseScore Studio and generates
MIDI files with sophisticated CC messages optimized for SWAM VST3 instruments.

This approach preserves articulations, dynamics, and expressions that are lost
in direct MIDI export.

Usage:
    python process_musicxml.py input.musicxml --instrument violin
    python process_musicxml.py input.musicxml --instrument saxophone --output custom.mid
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional

import mido
from music21 import converter, stream

from articulation_detector import (
    MusicXMLArticulationDetector,
    NoteArticulation,
    ArticulationType,
    DynamicChange,
    DynamicLevel
)
from swam_cc_mapper import SWAMCCMapper, SWAMInstrument


class MusicXMLToSWAM:
    """
    Converts MusicXML files to SWAM-optimized MIDI with articulation-aware CC messages.
    """
    
    def __init__(self, instrument: SWAMInstrument, ticks_per_beat: int = 480):
        """
        Initialize the converter.
        
        Args:
            instrument: SWAM instrument type
            ticks_per_beat: MIDI ticks per quarter note
        """
        self.instrument = instrument
        self.ticks_per_beat = ticks_per_beat
        self.cc_mapper = SWAMCCMapper(instrument)
        self.detector = MusicXMLArticulationDetector()
        # Track last CC values for smooth transitions
        self.last_cc11_value = 80  # Expression
        self.last_cc74_value = 64  # Brightness
        self.last_cc1_value = 0    # Modulation/vibrato
    
    def process_file(
        self,
        input_path: Path,
        output_path: Path,
        verbose: bool = False
    ) -> None:
        """
        Process a MusicXML file and generate SWAM-optimized MIDI.
        
        Args:
            input_path: Path to input MusicXML file
            output_path: Path to save output MIDI file
            verbose: Print detailed processing information
        """
        if verbose:
            print(f"Loading MusicXML file: {input_path}")
        
        try:
            score = converter.parse(input_path)
        except Exception as e:
            print(f"Error loading MusicXML file: {e}")
            sys.exit(1)
        
        if verbose:
            print(f"Analyzing articulations and dynamics...")
        
        # Extract articulations and dynamics
        note_articulations, dynamic_changes = self.detector.analyze_score(score)
        
        if verbose:
            print(f"  Found {len(note_articulations)} notes")
            print(f"  Found {len(dynamic_changes)} dynamic changes")
            
            # Count articulations
            art_counts = {}
            for note_art in note_articulations:
                for art in note_art.articulations:
                    art_counts[art.value] = art_counts.get(art.value, 0) + 1
            
            if art_counts:
                print(f"  Articulations detected:")
                for art_type, count in art_counts.items():
                    print(f"    - {art_type}: {count}")
        
        # Create MIDI file
        if verbose:
            print(f"Generating MIDI with SWAM CC messages...")
        
        midi_file = self._create_midi_from_articulations(
            note_articulations,
            dynamic_changes,
            score,
            verbose
        )
        
        # Save MIDI file
        if verbose:
            print(f"Saving MIDI file: {output_path}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        midi_file.save(output_path)
        
        if verbose:
            print("✓ Processing complete!")
    
    def _create_midi_from_articulations(
        self,
        note_articulations: List[NoteArticulation],
        dynamic_changes: List[DynamicChange],
        score: stream.Score,
        verbose: bool
    ) -> mido.MidiFile:
        """Create MIDI file from extracted articulation data."""
        
        midi_file = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = mido.MidiTrack()
        midi_file.tracks.append(track)
        
        # Add track name
        track.append(mido.MetaMessage('track_name', name='SWAM Processing', time=0))
        
        # Add tempo from score
        tempo = self._get_tempo_from_score(score)
        track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
        
        # Initialize default CCs
        track.extend(self._initialize_default_ccs())
        
        # Process each note with articulation-specific CC messages
        current_time = 0
        note_off_queue = []  # Track delayed note-offs for overlapping notes
        
        for i, note_art in enumerate(note_articulations):
            # Calculate delta time
            note_time_ticks = int(note_art.onset_time * self.ticks_per_beat)
            delta_time = note_time_ticks - current_time
            
            # Process any queued note-offs that should happen before this note
            while note_off_queue and note_off_queue[0][0] <= note_time_ticks:
                off_time, off_note, off_has_gliss = note_off_queue.pop(0)
                time_from_current = off_time - current_time
                
                # Add note off
                track.append(mido.Message(
                    'note_off',
                    note=off_note,
                    velocity=0,
                    time=time_from_current
                ))
                current_time = off_time
                
                # Reset portamento after glissando
                if off_has_gliss:
                    track.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=SWAMCCMapper.CC_PORTAMENTO,
                        value=0,
                        time=0
                    ))
            
            # Recalculate delta time after processing note-offs
            delta_time = note_time_ticks - current_time
            
            # Add CC messages for this note based on articulation
            cc_messages = self._generate_cc_for_note(note_art, delta_time)
            track.extend(cc_messages)
            
            # Add note on
            track.append(mido.Message(
                'note_on',
                note=note_art.pitch,
                velocity=note_art.velocity,
                time=0 if cc_messages else delta_time
            ))
            
            current_time = note_time_ticks
            
            # Calculate note off time
            duration_ticks = int(note_art.duration * self.ticks_per_beat)
            has_glissando = ArticulationType.GLISSANDO in note_art.articulations
            
            # Adjust duration for articulations
            if has_glissando:
                # Extend note to overlap with next note for glissando
                if i + 1 < len(note_articulations):
                    next_note_time = int(note_articulations[i + 1].onset_time * self.ticks_per_beat)
                    # Extend to overlap by 50% for more dramatic glissando slide
                    overlap_amount = int((next_note_time - note_time_ticks) * 0.5)
                    duration_ticks = (next_note_time - note_time_ticks) + overlap_amount
            elif ArticulationType.STACCATO in note_art.articulations:
                duration_ticks = int(duration_ticks * 0.35)  # 35% for integrated rhythmic flow
            elif ArticulationType.STACCATISSIMO in note_art.articulations:
                duration_ticks = int(duration_ticks * 0.20)  # 20% for very short notes
            
            # Queue the note off
            note_off_time = note_time_ticks + duration_ticks
            note_off_queue.append((note_off_time, note_art.pitch, has_glissando))
        
        # Process any remaining note-offs
        for off_time, off_note, off_has_gliss in note_off_queue:
            time_from_current = off_time - current_time
            track.append(mido.Message(
                'note_off',
                note=off_note,
                velocity=0,
                time=time_from_current
            ))
            current_time = off_time
            
            if off_has_gliss:
                track.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_PORTAMENTO,
                    value=0,
                    time=0
                ))
        
        # Add dynamic changes (crescendo/diminuendo)
        self._add_dynamic_changes(track, dynamic_changes)
        
        # Add end of track
        track.append(mido.MetaMessage('end_of_track', time=0))
        
        return midi_file
    
    def _generate_cc_for_note(
        self,
        note_art: NoteArticulation,
        delta_time: int
    ) -> List[mido.Message]:
        """Generate CC messages for a note based on its articulations."""
        messages = []
        
        # Base expression from dynamic level
        base_expression = note_art.dynamic_level.cc_value if note_art.dynamic_level else 80
        
        # Check for glissando - requires high portamento CC5
        if ArticulationType.GLISSANDO in note_art.articulations:
            # Set very high portamento for dramatic pitch slide
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_PORTAMENTO,
                value=110,  # Very high portamento for obvious glissando (was 80)
                time=delta_time
            ))
            
            # Enable legato for smooth slide
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_SUSTAIN,
                value=127,
                time=0
            ))
            
            # Add base expression
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_EXPRESSION,
                value=base_expression,
                time=0
            ))
            
            self.last_cc11_value = base_expression
            return messages
        
        # Check for staccato first - requires special CC spike pattern
        if ArticulationType.STACCATO in note_art.articulations:
            # Use SWAM staccato spike: quick CC11 peak then drop
            duration_ticks = int(note_art.duration * self.ticks_per_beat)
            staccato_messages = self.cc_mapper.apply_staccato(
                base_cc11=base_expression,
                spike_value=115,  # Sharp spike to 115 for crisp attack
                duration_ticks=duration_ticks
            )
            
            # Convert to mido messages with proper timing
            for time_offset, cc_msg in staccato_messages:
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=cc_msg.control,
                    value=cc_msg.value,
                    time=delta_time if not messages else time_offset
                ))
            
            # Add brightness for more attack
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BRIGHTNESS,
                value=min(127, 64 + 15),
                time=0
            ))
            
            # Update last CC11 value (staccato returns to base)
            self.last_cc11_value = base_expression
            
            return messages
        
        # Check for accent articulations - use CC spike patterns
        if ArticulationType.MARCATO in note_art.articulations:
            # Marcato: very strong attack with sustain
            marcato_messages = self.cc_mapper.apply_marcato(
                base_cc11=base_expression,
                peak_value=120
            )
            
            for time_offset, cc_msg in marcato_messages:
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=cc_msg.control,
                    value=cc_msg.value,
                    time=delta_time if not messages else time_offset
                ))
            
            # Add brightness
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BRIGHTNESS,
                value=min(127, 64 + 25),
                time=0
            ))
            
            # Update last CC11 value (marcato sustains at base)
            self.last_cc11_value = base_expression
            
            return messages
        
        if ArticulationType.ACCENT in note_art.articulations or ArticulationType.STRONG_ACCENT in note_art.articulations:
            # Accent: emphasized attack with sustain
            peak = 115 if ArticulationType.STRONG_ACCENT in note_art.articulations else 110
            accent_messages = self.cc_mapper.apply_accent(
                base_cc11=base_expression,
                peak_value=peak
            )
            
            for time_offset, cc_msg in accent_messages:
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=cc_msg.control,
                    value=cc_msg.value,
                    time=delta_time if not messages else time_offset
                ))
            
            # Add brightness
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BRIGHTNESS,
                value=min(127, 64 + 20),
                time=0
            ))
            
            # Update last CC11 value (accent sustains at base)
            self.last_cc11_value = base_expression
            
            return messages
        
        # For other articulations, modify based on type
        expression_value = base_expression
        brightness_value = 64
        modulation_value = 0
        
        for art in note_art.articulations:
            if art == ArticulationType.STACCATISSIMO:
                expression_value = max(20, expression_value - 30)
                brightness_value = min(127, brightness_value + 25)
            
            elif art == ArticulationType.TENUTO:
                expression_value = min(127, expression_value + 5)
        
        # Add vibrato for longer notes
        if note_art.duration >= 2.0:  # Half note or longer
            modulation_value = 64  # Moderate vibrato
        elif note_art.duration >= 1.0:  # Quarter note
            modulation_value = 48  # Light vibrato
        
        # Add expression CC with smooth transition from previous value
        if abs(expression_value - self.last_cc11_value) > 5:
            # Significant change - create smooth ramp
            ramp_duration = min(delta_time, 30)  # Ramp over available time, max 30 ticks
            ramp_steps = max(2, min(4, ramp_duration // 8))  # 2-4 steps depending on time
            
            cc11_ramp = self.cc_mapper._create_ramp(
                cc_number=SWAMCCMapper.CC_EXPRESSION,
                start_value=self.last_cc11_value,
                end_value=expression_value,
                duration_ticks=ramp_duration,
                steps=ramp_steps
            )
            
            # Add ramped messages with adjusted timing
            for i, (time_offset, msg) in enumerate(cc11_ramp):
                if i == 0:
                    # First message uses the delta_time
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=msg.control,
                        value=msg.value,
                        time=delta_time
                    ))
                else:
                    # Subsequent messages use their offsets
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=msg.control,
                        value=msg.value,
                        time=time_offset
                    ))
        else:
            # Small or no change - direct transition
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_EXPRESSION,
                value=expression_value,
                time=delta_time
            ))
        
        # Update tracked value
        self.last_cc11_value = expression_value
        
        # Add brightness CC with smooth transition
        if brightness_value != 64:
            if abs(brightness_value - self.last_cc74_value) > 10:
                # Significant brightness change - smooth it
                cc74_ramp = self.cc_mapper._create_ramp(
                    cc_number=SWAMCCMapper.CC_BRIGHTNESS,
                    start_value=self.last_cc74_value,
                    end_value=brightness_value,
                    duration_ticks=10,
                    steps=2
                )
                for time_offset, msg in cc74_ramp:
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=msg.control,
                        value=msg.value,
                        time=time_offset
                    ))
            else:
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BRIGHTNESS,
                    value=brightness_value,
                    time=0
                ))
            self.last_cc74_value = brightness_value
        
        # Add vibrato CC with smooth onset
        if modulation_value > 0:
            if self.last_cc1_value == 0:
                # Starting vibrato from 0 - gradually introduce it
                cc1_ramp = self.cc_mapper._create_ramp(
                    cc_number=SWAMCCMapper.CC_MODULATION,
                    start_value=0,
                    end_value=modulation_value,
                    duration_ticks=60,  # Gradual vibrato onset (1/8 note)
                    steps=4
                )
                for time_offset, msg in cc1_ramp:
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=msg.control,
                        value=msg.value,
                        time=time_offset
                    ))
            else:
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_MODULATION,
                    value=modulation_value,
                    time=0
                ))
            self.last_cc1_value = modulation_value
        
        # Add legato (sustain) for slurred notes
        if note_art.in_slur:
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_SUSTAIN,
                value=127,
                time=0
            ))
        else:
            # Release sustain if not in slur
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_SUSTAIN,
                value=0,
                time=0
            ))
        
        # Add breath for saxophone
        if self.instrument == SWAMInstrument.SAXOPHONE:
            breath_value = expression_value  # Link breath to expression
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BREATH,
                value=breath_value,
                time=0
            ))
        
        return messages
    
    def _initialize_default_ccs(self) -> List[mido.Message]:
        """Initialize default CC values at the start of the track."""
        messages = []
        
        # Expression
        messages.append(mido.Message(
            'control_change',
            channel=0,
            control=SWAMCCMapper.CC_EXPRESSION,
            value=80,
            time=0
        ))
        
        # Modulation (vibrato)
        messages.append(mido.Message(
            'control_change',
            channel=0,
            control=SWAMCCMapper.CC_MODULATION,
            value=0,
            time=0
        ))
        
        # Brightness
        messages.append(mido.Message(
            'control_change',
            channel=0,
            control=SWAMCCMapper.CC_BRIGHTNESS,
            value=64,
            time=0
        ))
        
        # Sustain
        messages.append(mido.Message(
            'control_change',
            channel=0,
            control=SWAMCCMapper.CC_SUSTAIN,
            value=0,
            time=0
        ))
        
        # Breath (saxophone only)
        if self.instrument == SWAMInstrument.SAXOPHONE:
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BREATH,
                value=64,
                time=0
            ))
        
        return messages
    
    def _add_dynamic_changes(
        self,
        track: mido.MidiTrack,
        dynamic_changes: List[DynamicChange]
    ):
        """Add crescendo/diminuendo CC messages to the track."""
        # This would be implemented by inserting CC messages at appropriate times
        # For now, the expression changes are handled per-note
        pass
    
    def _get_tempo_from_score(self, score: stream.Score) -> int:
        """Extract tempo from score, default to 120 BPM."""
        try:
            tempo_marks = score.flatten().getElementsByClass('MetronomeMark')
            if len(tempo_marks) > 0:
                bpm = tempo_marks[0].number
                return mido.bpm2tempo(bpm)
        except:
            pass
        
        return mido.bpm2tempo(120)  # Default 120 BPM


def main():
    parser = argparse.ArgumentParser(
        description="Process MusicXML files from MuseScore for SWAM instruments"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input MusicXML file path (.musicxml or .xml)"
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
    processor = MusicXMLToSWAM(instrument)
    processor.process_file(input_path, output_path, args.verbose)
    
    print(f"✓ Processed file saved to: {output_path}")


if __name__ == "__main__":
    main()
