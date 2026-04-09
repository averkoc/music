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
import json
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
from humanizer import (
    SWAMHumanizer,
    HumanizationConfig,
    create_default_humanizer,
    create_subtle_humanizer,
    create_aggressive_humanizer
)


class MusicXMLToSWAM:
    """
    Converts MusicXML files to SWAM-optimized MIDI with articulation-aware CC messages.
    """
    
    def __init__(self, instrument: SWAMInstrument, ticks_per_beat: int = 480, humanizer: SWAMHumanizer = None):
        """
        Initialize the converter.
        
        Args:
            instrument: SWAM instrument type
            ticks_per_beat: MIDI ticks per quarter note
            humanizer: Optional humanizer for natural performance variation
        """
        self.instrument = instrument
        self.ticks_per_beat = ticks_per_beat
        self.cc_mapper = SWAMCCMapper(instrument)
        self.detector = MusicXMLArticulationDetector()
        self.humanizer = humanizer  # Can be None for precise mode
        
        # Load config from swam_config.json
        config_path = Path(__file__).parent.parent / "config" / "swam_config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Get instrument-specific config
        instrument_name = instrument.value  # 'violin' or 'saxophone'
        self.instrument_config = self.config.get('instruments', {}).get(instrument_name, {})
        
        # Track last CC values for smooth transitions
        self.last_cc11_value = 80  # Expression
        self.last_cc74_value = 64  # Harmonics
        self.last_cc1_value = 0    # Modulation/vibrato
        self.last_cc20_value = 64  # Bow Force
        self.last_cc21_value = 64  # Bow Position
        
        # Track previous pitch for Phase 1 interval-aware portamento
        self.prev_pitch = None
    
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
        note_off_queue = []  # Track delayed note-offs: (time, note, has_gliss, note_off_velocity)
        total_notes = len(note_articulations)
        tempo_bpm = mido.tempo2bpm(tempo)
        
        for i, note_art in enumerate(note_articulations):
            # Calculate delta time
            note_time_ticks = int(note_art.onset_time * self.ticks_per_beat)
            
            # Apply humanization to timing if enabled (but ensure notes don't go backwards)
            if self.humanizer:
                humanized_time = self.humanizer.humanize_timing(
                    note_time_ticks,
                    self.ticks_per_beat,
                    tempo_bpm
                )
                # Ensure this note doesn't come before current time
                note_time_ticks = max(current_time + 1, humanized_time)
            
            delta_time = note_time_ticks - current_time
            
            # Process any queued note-offs that should happen before this note
            while note_off_queue and note_off_queue[0][0] <= note_time_ticks:
                off_time, off_note, off_has_gliss, off_velocity = note_off_queue.pop(0)
                # Ensure note-off doesn't go backwards
                off_time = max(current_time, off_time)
                time_from_current = off_time - current_time
                
                # Add note off with articulation-specific velocity
                track.append(mido.Message(
                    'note_off',
                    note=off_note,
                    velocity=off_velocity,  # Use articulation-specific velocity
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
            
            # Recalculate delta time after processing note-offs, ensure non-negative
            delta_time = max(0, note_time_ticks - current_time)
            
            # Add CC messages for this note based on articulation
            # Pass previous pitch for Phase 1 portamento
            cc_messages = self._generate_cc_for_note(note_art, delta_time, i, total_notes)
            
            # Send CC messages just before note-on (at same tick, processed first by MIDI spec)
            # All CCs have time=0 except first which gets the delta_time
            if cc_messages:
                # First CC gets all the delta time
                cc_messages[0].time = delta_time
                # All other CCs happen at time=0 (same tick, but ordered before note-on)
                for i_cc in range(1, len(cc_messages)):
                    cc_messages[i_cc].time = 0
                
                track.extend(cc_messages)
            
            # Update previous pitch for next note (Phase 1 portamento)
            self.prev_pitch = note_art.pitch
            
            # Apply humanization to velocity if enabled
            velocity = note_art.velocity
            if self.humanizer:
                velocity = self.humanizer.humanize_velocity(velocity)
            
            # Add note on at time=0 (same tick as CCs, but after them in message order)
            track.append(mido.Message(
                'note_on',
                note=note_art.pitch,
                velocity=velocity,
                time=0 if cc_messages else delta_time
            ))
            
            current_time = note_time_ticks
            
            # Calculate note off time
            duration_ticks = int(note_art.duration * self.ticks_per_beat)
            has_glissando = ArticulationType.GLISSANDO in note_art.articulations
            has_vibrato = ArticulationType.VIBRATO in note_art.articulations
            
            # NOTE: Vibrato jitter during sustain disabled due to MIDI timing issues
            # The jitter messages were accumulating time offsets and disrupting rhythm
            # Vibrato ramp still works (happens before note-on), but continuous jitter
            # during sustain needs a different implementation approach
            # TODO: Re-implement jitter without disrupting note timing
            
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
            
            # Apply humanization to duration if enabled
            if self.humanizer and not has_glissando:  # Don't humanize glissando timing
                duration_ticks = self.humanizer.humanize_duration(duration_ticks)
            
            # Determine note-off velocity based on articulation (for KeyLab mk3 and physical modeling)
            note_off_velocity = 64  # Default medium bow lift
            
            if ArticulationType.STACCATO in note_art.articulations:
                note_off_velocity = 110  # Sharp bow stop
            elif ArticulationType.STACCATISSIMO in note_art.articulations:
                note_off_velocity = 120  # Very sharp bow stop
            elif ArticulationType.MARCATO in note_art.articulations:
                note_off_velocity = 90  # Emphasized release
            elif ArticulationType.ACCENT in note_art.articulations or ArticulationType.STRONG_ACCENT in note_art.articulations:
                note_off_velocity = 80  # Moderate bow stop
            elif note_art.in_slur:
                note_off_velocity = 20  # Very smooth bow connection
            elif ArticulationType.TENUTO in note_art.articulations:
                note_off_velocity = 30  # Gentle bow lift
            elif has_glissando:
                note_off_velocity = 10  # Seamless slide (bow stays on string)
            
            # Queue the note off with velocity
            note_off_time = note_time_ticks + duration_ticks
            note_off_queue.append((note_off_time, note_art.pitch, has_glissando, note_off_velocity))
        
        # Process any remaining note-offs
        for off_time, off_note, off_has_gliss, off_velocity in note_off_queue:
            # Ensure note-off doesn't go backwards
            off_time = max(current_time, off_time)
            time_from_current = off_time - current_time
            track.append(mido.Message(
                'note_off',
                note=off_note,
                velocity=off_velocity,  # Use articulation-specific velocity
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
        delta_time: int,
        note_index: int = 0,
        total_notes: int = 1
    ) -> List[mido.Message]:
        """Generate CC messages for a note based on its articulations."""
        messages = []
        
        # Base expression from dynamic level
        base_expression = note_art.dynamic_level.cc_value if note_art.dynamic_level else 80
        
        # Apply humanization to expression if enabled
        if self.humanizer and self.humanizer.should_add_expression_flutter():
            base_expression = self.humanizer.humanize_expression(base_expression)
        
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
            
            # Add coupled CC2 (bow pressure)
            cc2_value = self.cc_mapper._cc11_to_cc2(base_expression)
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BREATH,
                value=cc2_value,
                time=0
            ))
            
            self.last_cc11_value = base_expression
            return messages
        
        # Check for vibrato articulation mark - use delayed vibrato from config
        if ArticulationType.VIBRATO in note_art.articulations:
            # Get vibrato config
            vibrato_config = self.instrument_config.get('articulations', {}).get('vibrato_mark', {})
            
            # Check minimum duration (default 0.5 seconds = 2 quarter notes)
            min_duration = vibrato_config.get('min_duration_seconds', 0.5) * 2  # Convert to quarter notes
            if note_art.duration < min_duration:
                # Note too short for vibrato - skip it
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_EXPRESSION,
                    value=base_expression,
                    time=delta_time
                ))
                # Add coupled CC2
                cc2_value = self.cc_mapper._cc11_to_cc2(base_expression)
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BREATH,
                    value=cc2_value,
                    time=0
                ))
                self.last_cc11_value = base_expression
                return messages
            
            # Get tempo for tick conversion
            tempo_bpm = 120  # Default tempo (could be extracted from score)
            ticks_per_beat = self.ticks_per_beat
            ms_per_beat = 60000 / tempo_bpm
            
            # Determine pitch-dependent vibrato parameters
            pitch_config = vibrato_config.get('pitch_dependent', {})
            if pitch_config.get('enabled', True):
                # Get MIDI pitch (C4 = 60, D4 = 62, D5 = 74)
                pitch = note_art.pitch
                low_threshold = 62  # D4
                high_threshold = 74  # D5
                
                if pitch < low_threshold:
                    # Low notes: wider, slower vibrato
                    cc1_target = pitch_config.get('low_notes', {}).get('cc1_depth', 50)
                    cc17_target = pitch_config.get('low_notes', {}).get('cc17_rate', 60)
                elif pitch > high_threshold:
                    # High notes: narrower, faster vibrato
                    cc1_target = pitch_config.get('high_notes', {}).get('cc1_depth', 40)
                    cc17_target = pitch_config.get('high_notes', {}).get('cc17_rate', 75)
                else:
                    # Mid notes: balanced vibrato
                    cc1_target = pitch_config.get('mid_notes', {}).get('cc1_depth', 45)
                    cc17_target = pitch_config.get('mid_notes', {}).get('cc17_rate', 67)
            else:
                # Fixed vibrato depth/rate
                cc1_target = vibrato_config.get('cc1_target', 45)
                cc17_target = vibrato_config.get('cc17_target', 67)
            
            # Get timing parameters
            delay_ms = vibrato_config.get('delay_ms', 300)
            ramp_ms = vibrato_config.get('ramp_duration_ms', 200)
            delay_ticks = int((delay_ms / ms_per_beat) * ticks_per_beat)
            ramp_ticks = int((ramp_ms / ms_per_beat) * ticks_per_beat)
            
            # Set initial vibrato state (no delay/ramp before note-on to preserve rhythm)
            # CC1 starts at 0, CC17 at target rate
            # Vibrato will be developed later if we re-implement sustain modulation
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_MODULATION,  # CC1
                value=0,
                time=delta_time
            ))
            
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=17,  # CC17 - Vibrato Rate
                value=cc17_target,
                time=0
            ))
            
            # Simple immediate vibrato (no delay/ramp for timing reasons)
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_MODULATION,
                value=cc1_target,
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
            
            # Add coupled CC2 (bow pressure)
            cc2_value = self.cc_mapper._cc11_to_cc2(base_expression)
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BREATH,
                value=cc2_value,
                time=0
            ))
            
            self.last_cc11_value = base_expression
            self.last_cc1_value = cc1_target  # Track vibrato depth
            
            # Store vibrato info for jitter generation (will be added after note-on)
            note_art._vibrato_targets = (cc1_target, cc17_target, vibrato_config)
            
            return messages
        
        # Apply default baseline vibrato to sustained notes without explicit vibrato marks
        # (Real violinists use vibrato as fundamental tone production)
        default_vibrato_config = self.instrument_config.get('articulations', {}).get('default_vibrato', {})
        if default_vibrato_config.get('enabled', True):
            # Check duration threshold
            min_duration = default_vibrato_config.get('min_duration_quarters', 1.0)
            if note_art.duration >= min_duration:
                # Check for excluded articulations
                excluded_types = default_vibrato_config.get('exclude_articulations', ['staccato', 'staccatissimo', 'spiccato'])
                excluded_enum = []
                if 'staccato' in excluded_types:
                    excluded_enum.append(ArticulationType.STACCATO)
                if 'staccatissimo' in excluded_types:
                    excluded_enum.append(ArticulationType.STACCATISSIMO)
                if 'spiccato' in excluded_types:
                    excluded_enum.append(ArticulationType.SPICCATO)
                
                # Apply baseline vibrato if no excluded articulations present
                if not any(art in note_art.articulations for art in excluded_enum):
                    # Get tempo for tick conversion
                    tempo_bpm = 120
                    ticks_per_beat = self.ticks_per_beat
                    ms_per_beat = 60000 / tempo_bpm
                    
                    # Determine pitch-dependent baseline vibrato
                    pitch_config = default_vibrato_config.get('pitch_dependent', {})
                    if pitch_config.get('enabled', True):
                        pitch = note_art.pitch
                        low_threshold = 62  # D4
                        high_threshold = 74  # D5
                        
                        if pitch < low_threshold:
                            cc1_target = pitch_config.get('low_notes', {}).get('cc1_depth', 28)
                            cc17_target = pitch_config.get('low_notes', {}).get('cc17_rate', 62)
                        elif pitch > high_threshold:
                            cc1_target = pitch_config.get('high_notes', {}).get('cc1_depth', 22)
                            cc17_target = pitch_config.get('high_notes', {}).get('cc17_rate', 68)
                        else:
                            cc1_target = pitch_config.get('mid_notes', {}).get('cc1_depth', 25)
                            cc17_target = pitch_config.get('mid_notes', {}).get('cc17_rate', 65)
                    else:
                        cc1_target = default_vibrato_config.get('cc1_target', 25)
                        cc17_target = default_vibrato_config.get('cc17_target', 65)
                    
                    # Get timing parameters
                    delay_ms = default_vibrato_config.get('delay_ms', 250)
                    ramp_ms = default_vibrato_config.get('ramp_duration_ms', 200)
                    delay_ticks = int((delay_ms / ms_per_beat) * ticks_per_beat)
                    ramp_ticks = int((ramp_ms / ms_per_beat) * ticks_per_beat)
                    
                    # Set baseline vibrato state (immediate, no delay/ramp for timing)
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=SWAMCCMapper.CC_MODULATION,  # CC1
                        value=cc1_target,  # Set immediately to baseline level
                        time=delta_time
                    ))
                    
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=17,  # CC17 - Vibrato Rate
                        value=cc17_target,
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
                    
                    # Add coupled CC2 (bow pressure)
                    cc2_value = self.cc_mapper._cc11_to_cc2(base_expression)
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=SWAMCCMapper.CC_BREATH,
                        value=cc2_value,
                        time=0
                    ))
                    
                    self.last_cc11_value = base_expression
                    self.last_cc1_value = cc1_target
                    
                    # Store vibrato info for jitter
                    note_art._vibrato_targets = (cc1_target, cc17_target, default_vibrato_config)
                    
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
            
            # Add harmonics for more attack
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_HARMONICS,
                value=min(127, 64 + 15),
                time=0
            ))
            
            # Add bow controls for staccato (violin only)
            if self.instrument == SWAMInstrument.VIOLIN:
                # Dynamic bow force based on expression + staccato character
                import random
                staccato_force = int(60 + (base_expression - 20) * 0.25) + random.randint(-3, 3)
                staccato_force = max(55, min(85, staccato_force))
                
                # Bow position: toward bridge for brightness + slight variation
                staccato_position = 70 + random.randint(-2, 2)
                
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BOW_FORCE,
                    value=staccato_force,
                    time=0
                ))
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BOW_POSITION,
                    value=staccato_position,
                    time=0
                ))
                self.last_cc20_value = staccato_force
                self.last_cc21_value = staccato_position
            
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
            
            # Add harmonics
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_HARMONICS,
                value=min(127, 64 + 25),
                time=0
            ))
            
            # Add bow controls for marcato (violin only)
            if self.instrument == SWAMInstrument.VIOLIN:
                # Heavy bow force for marcato + variation
                import random
                marcato_force = int(85 + (base_expression - 20) * 0.15) + random.randint(-4, 4)
                marcato_force = max(80, min(105, marcato_force))
                
                # Toward bridge for power + variation
                marcato_position = 68 + random.randint(-3, 3)
                
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BOW_FORCE,
                    value=marcato_force,
                    time=0
                ))
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BOW_POSITION,
                    value=marcato_position,
                    time=0
                ))
                self.last_cc20_value = marcato_force
                self.last_cc21_value = marcato_position
            
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
            
            # Add harmonics
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_HARMONICS,
                value=min(127, 64 + 20),
                time=0
            ))
            
            # Add bow controls for accent (violin only)
            if self.instrument == SWAMInstrument.VIOLIN:
                # Accent bow force depends on accent strength + variation
                import random
                is_strong = ArticulationType.STRONG_ACCENT in note_art.articulations
                accent_base = 78 if is_strong else 72
                accent_force = int(accent_base + (base_expression - 20) * 0.2) + random.randint(-4, 4)
                accent_force = max(65, min(95, accent_force))
                
                # Slightly toward bridge + variation
                accent_position = 66 + random.randint(-3, 3)
                
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BOW_FORCE,
                    value=accent_force,
                    time=0
                ))
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BOW_POSITION,
                    value=accent_position,
                    time=0
                ))
                self.last_cc20_value = accent_force
                self.last_cc21_value = accent_position
            
            # Update last CC11 value (accent sustains at base)
            self.last_cc11_value = base_expression
            
            return messages
        
        # For other articulations, modify based on type
        expression_value = base_expression
        harmonics_value = 64
        modulation_value = 0
        bow_force = None  # Will be calculated if needed (don't reset to 64)
        bow_position = None  # Will be calculated if needed (don't reset to 64)
        
        # Check if this is a "plain" note without special articulation handling
        has_special_articulation = (
            ArticulationType.STACCATISSIMO in note_art.articulations or
            ArticulationType.TENUTO in note_art.articulations
        )
        
        # Apply Phase 1 CC11 envelope for plain notes (no special articulation)
        # This gives natural bow dynamics instead of flat CC11
        # Note: For MusicXML workflow, we use a simplified envelope approach
        # that sets initial CC values before note-on, rather than scheduling
        # messages throughout the note duration.
        if not has_special_articulation and len(note_art.articulations) == 0:
            # Add Phase 1 interval-aware portamento before the note
            portamento_config = self.instrument_config.get('portamento', {})
            if portamento_config.get('enabled', True) and self.prev_pitch is not None:
                portamento_amount = self.cc_mapper.calculate_portamento_amount(
                    self.prev_pitch,
                    note_art.pitch,
                    base_amount=portamento_config.get('base_amount', 60)
                )
                
                if portamento_amount > 0:
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=SWAMCCMapper.CC_PORTAMENTO,
                        value=portamento_amount,
                        time=delta_time
                    ))
                    delta_time = 0  # Portamento consumed the delta_time
                    
                    # Reset portamento immediately (tighter timing)
                    messages.append(mido.Message(
                        'control_change',
                        channel=0,
                        control=SWAMCCMapper.CC_PORTAMENTO,
                        value=0,
                        time=0  # Reset immediately with note-on
                    ))
            
            # Phase 1 simplified envelope: Use smooth ramp approach
            # Set expression slightly below target, let SWAM's envelope do the rest
            # This preserves attack timing while avoiding flat CC11
            attack_value = int(base_expression * 0.9)  # Start at 90% (more subtle)
            
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_EXPRESSION,
                value=attack_value,
                time=delta_time if not messages else 0
            ))
            
            # Add coupled CC2 (bow pressure) with CC11
            cc2_value = self.cc_mapper._cc11_to_cc2(attack_value)
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BREATH,
                value=cc2_value,
                time=0
            ))
            
            # Track last CC11 value
            self.last_cc11_value = attack_value
            
            return messages
        
        # For articulated notes (staccatissimo, tenuto), apply articulation modifiers
        for art in note_art.articulations:
            if art == ArticulationType.STACCATISSIMO:
                expression_value = max(20, expression_value - 30)
                harmonics_value = min(127, harmonics_value + 25)
                bow_force = 75  # Light, quick bow for staccatissimo
                bow_position = 75  # Closer to bridge for brightness
            
            elif art == ArticulationType.TENUTO:
                expression_value = min(127, expression_value + 5)
                bow_force = min(100, int(expression_value * 0.9))  # Sustained pressure
                bow_position = 60  # Slightly toward fingerboard for warmth
        
        # Automatic vibrato disabled - use explicit vibrato articulation marks instead
        # If you want automatic vibrato, add it in MuseScore using vibrato marks
        # (keeping this commented code for reference)
        # if note_art.duration >= 2.0:  # Half note or longer
        #     modulation_value = 64  # Moderate vibrato
        # elif note_art.duration >= 1.0:  # Quarter note
        #     modulation_value = 48  # Light vibrato
        
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
                
                # Add coupled CC2 (bow pressure) for each CC11 value
                cc2_value = self.cc_mapper._cc11_to_cc2(msg.value)
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=SWAMCCMapper.CC_BREATH,
                    value=cc2_value,
                    time=0
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
            
            # Add coupled CC2 (bow pressure)
            cc2_value = self.cc_mapper._cc11_to_cc2(expression_value)
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BREATH,
                value=cc2_value,
                time=0
            ))
        
        # Update tracked value
        self.last_cc11_value = expression_value
        
        # Add harmonics CC with smooth transition
        if harmonics_value != 64:
            if abs(harmonics_value - self.last_cc74_value) > 10:
                # Significant harmonics change - smooth it
                cc74_ramp = self.cc_mapper._create_ramp(
                    cc_number=SWAMCCMapper.CC_HARMONICS,
                    start_value=self.last_cc74_value,
                    end_value=harmonics_value,
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
                    control=SWAMCCMapper.CC_HARMONICS,
                    value=harmonics_value,
                    time=0
                ))
            self.last_cc74_value = harmonics_value
        
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
        elif self.last_cc1_value > 0:
            # Turn off vibrato if it was on previously
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_MODULATION,
                value=0,
                time=0
            ))
            self.last_cc1_value = 0
        
        # Add bow force and position (violin only)
        if self.instrument == SWAMInstrument.VIOLIN:
            # Couple bow force to expression for normal notes
            if bow_force is None:  # Not set by articulation - calculate it
                # Map expression (20-127) to bow force (35-105)
                # Soft playing = light bow, loud playing = heavy bow
                bow_force = int(35 + (expression_value - 20) * 0.65)
                bow_force = max(35, min(105, bow_force))
                
                # Add subtle random variation for human feel (+/- 5)
                import random
                variation = random.randint(-5, 5)
                bow_force = max(35, min(105, bow_force + variation))
            
            # Adjust bow position based on phrase position (slight drift for realism)
            if bow_position is None:  # Not set by articulation - calculate it
                # Add subtle variation based on velocity for natural movement
                velocity_factor = (note_art.velocity - 64) / 127.0  # -0.5 to +0.5 range
                bow_position = int(64 + velocity_factor * 10)  # 59-69 range
                bow_position = max(55, min(75, bow_position))
            
            # Add bow force CC (always send for dynamic expression)
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BOW_FORCE,
                value=bow_force,
                time=0
            ))
            self.last_cc20_value = bow_force
            
            # Add bow position CC (always send for natural bow movement)
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BOW_POSITION,
                value=bow_position,
                time=0
            ))
            self.last_cc21_value = bow_position
        
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
    
    def _generate_vibrato_jitter(
        self,
        note_art: NoteArticulation,
        duration_ticks: int,
        already_elapsed_ticks: int
    ) -> List[mido.Message]:
        """
        Generate continuous jitter CC messages during vibrato sustain.
        
        Args:
            note_art: Note articulation data (must have _vibrato_targets attribute)
            duration_ticks: Total note duration in ticks
            already_elapsed_ticks: Ticks already used for vibrato ramp
            
        Returns:
            List of CC messages with timing offsets for jitter during sustain
        """
        import random
        
        messages = []
        
        # Check if vibrato jitter is configured
        if not hasattr(note_art, '_vibrato_targets'):
            return messages
        
        cc1_target, cc17_target, vibrato_config = note_art._vibrato_targets
        jitter_config = vibrato_config.get('jitter', {})
        
        if not jitter_config.get('enabled', True):
            return messages
        
        # Get jitter parameters
        cc1_range = jitter_config.get('cc1_range', 5)
        cc17_range = jitter_config.get('cc17_range', 3)
        interval_ms = jitter_config.get('interval_ms', 50)
        
        # Convert interval to ticks
        tempo_bpm = 120
        ms_per_beat = 60000 / tempo_bpm
        interval_ticks = int((interval_ms / ms_per_beat) * self.ticks_per_beat)
        
        # Calculate remaining sustain time
        remaining_ticks = duration_ticks - already_elapsed_ticks
        
        if remaining_ticks <= 0:
            return messages
        
        # Generate jitter messages at intervals
        current_offset = interval_ticks
        
        while current_offset < remaining_ticks:
            # Add jitter to CC1 (depth)
            cc1_jitter = random.randint(-cc1_range, cc1_range)
            cc1_value = max(0, min(127, cc1_target + cc1_jitter))
            
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_MODULATION,  # CC1
                value=cc1_value,
                time=current_offset if len(messages) == 0 else interval_ticks
            ))
            
            # Add jitter to CC17 (rate) - less frequently (every other CC1 change)
            if len(messages) % 2 == 1:
                cc17_jitter = random.randint(-cc17_range, cc17_range)
                cc17_value = max(0, min(127, cc17_target + cc17_jitter))
                
                messages.append(mido.Message(
                    'control_change',
                    channel=0,
                    control=17,  # CC17 - Vibrato Rate
                    value=cc17_value,
                    time=0
                ))
            
            current_offset += interval_ticks
        
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
        
        # Bow pressure (coupled to expression)
        messages.append(mido.Message(
            'control_change',
            channel=0,
            control=SWAMCCMapper.CC_BREATH,
            value=self.cc_mapper._cc11_to_cc2(80),
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
        
        # Harmonics
        messages.append(mido.Message(
            'control_change',
            channel=0,
            control=SWAMCCMapper.CC_HARMONICS,
            value=64,
            time=0
        ))
        
        # Bow Force (strings only)
        if self.instrument == SWAMInstrument.VIOLIN:
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BOW_FORCE,
                value=64,  # Neutral bow pressure
                time=0
            ))
        
        # Bow Position (strings only)
        if self.instrument == SWAMInstrument.VIOLIN:
            messages.append(mido.Message(
                'control_change',
                channel=0,
                control=SWAMCCMapper.CC_BOW_POSITION,
                value=64,  # Neutral bow position
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
        "--humanize",
        type=str,
        choices=["none", "subtle", "default", "aggressive"],
        default="none",
        help="Humanization level: none (precise), subtle (light variation), default (natural), aggressive (obvious variation)"
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
    
    # Create humanizer based on flag
    humanizer = None
    if args.humanize == "subtle":
        humanizer = create_subtle_humanizer()
        if args.verbose:
            print("Humanization: Subtle (light variation)")
    elif args.humanize == "default":
        humanizer = create_default_humanizer()
        if args.verbose:
            print("Humanization: Default (natural performance)")
    elif args.humanize == "aggressive":
        humanizer = create_aggressive_humanizer()
        if args.verbose:
            print("Humanization: Aggressive (obvious variation)")
    else:
        if args.verbose:
            print("Humanization: None (precise)")
    
    # Process the file
    processor = MusicXMLToSWAM(instrument, humanizer=humanizer)
    processor.process_file(input_path, output_path, args.verbose)
    
    print(f"✓ Processed file saved to: {output_path}")


if __name__ == "__main__":
    main()
