"""
Articulation Mapper

Maps detected articulations to SWAM CC messages using configuration.
Loads settings from swam_config.json and applies them via SWAMCCMapper.
"""

import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
import mido
from swam_cc_mapper import SWAMCCMapper, SWAMInstrument
from articulation_detector import ArticulationType


class ArticulationMapper:
    """
    Maps articulations to SWAM CC messages using configuration.
    """
    
    def __init__(self, instrument: SWAMInstrument, config_path: str = None):
        """
        Initialize the articulation mapper.
        
        Args:
            instrument: SWAM instrument type
            config_path: Path to swam_config.json (optional)
        """
        self.instrument = instrument
        self.mapper = SWAMCCMapper(instrument)
        
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "swam_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Get instrument-specific settings
        instrument_name = instrument.value
        self.instrument_config = self.config['instruments'][instrument_name]
        self.articulation_config = self.instrument_config['articulations']
        self.dynamics_config = self.instrument_config['dynamics']
    
    def apply_articulation(
        self,
        articulation_type: ArticulationType,
        base_cc11: int,
        note_duration_ticks: int,
        tempo_bpm: int = 120
    ) -> List[Tuple[int, mido.Message]]:
        """
        Apply an articulation based on configuration.
        
        Args:
            articulation_type: Type of articulation to apply
            base_cc11: Baseline CC11 expression value
            note_duration_ticks: Duration of the note in MIDI ticks
            tempo_bpm: Tempo for timing calculations
            
        Returns:
            List of (time_offset, message) tuples
        """
        messages = []
        
        # Map articulation types to handlers
        if articulation_type == ArticulationType.STACCATO:
            messages = self._apply_staccato(base_cc11, note_duration_ticks)
        
        elif articulation_type == ArticulationType.VIBRATO:
            messages = self._apply_vibrato(tempo_bpm)
        
        elif articulation_type == ArticulationType.SUL_PONTICELLO:
            messages = self._apply_sul_ponticello()
        
        elif articulation_type == ArticulationType.SUL_TASTO:
            messages = self._apply_sul_tasto()
        
        elif articulation_type == ArticulationType.SLUR or articulation_type == ArticulationType.LEGATO:
            messages = self._apply_slur()
        
        elif articulation_type == ArticulationType.ACCENT:
            messages = self._apply_accent(base_cc11)
        
        elif articulation_type == ArticulationType.CRESCENDO:
            messages = self._apply_crescendo(base_cc11, note_duration_ticks)
        
        elif articulation_type == ArticulationType.DIMINUENDO:
            messages = self._apply_diminuendo(base_cc11, note_duration_ticks)
        
        elif articulation_type == ArticulationType.GLISSANDO:
            messages = self._apply_glissando()
        
        return messages
    
    def _apply_staccato(
        self,
        base_cc11: int,
        note_duration_ticks: int
    ) -> List[Tuple[int, mido.Message]]:
        """Apply staccato articulation from config."""
        config = self.articulation_config.get('staccato', {})
        spike_value = config.get('cc11_spike', 105)
        
        return self.mapper.apply_staccato(
            base_cc11=base_cc11,
            spike_value=spike_value,
            duration_ticks=note_duration_ticks
        )
    
    def _apply_vibrato(self, tempo_bpm: int) -> List[Tuple[int, mido.Message]]:
        """Apply delayed vibrato from config."""
        config = self.articulation_config.get('vibrato_mark', {})
        
        # Convert milliseconds to ticks (480 ticks per quarter note assumed)
        delay_ms = config.get('delay_ms', 500)
        ramp_ms = config.get('ramp_duration_ms', 300)
        target = config.get('cc1_target', 64)
        
        ticks_per_beat = 480
        ms_per_beat = 60000 / tempo_bpm
        delay_ticks = int((delay_ms / ms_per_beat) * ticks_per_beat)
        ramp_ticks = int((ramp_ms / ms_per_beat) * ticks_per_beat)
        
        return self.mapper.apply_vibrato_delayed(
            target_depth=target,
            delay_ticks=delay_ticks,
            ramp_duration_ticks=ramp_ticks,
            steps=8
        )
    
    def _apply_sul_ponticello(self) -> List[Tuple[int, mido.Message]]:
        """Apply sul ponticello articulation from config."""
        config = self.articulation_config.get('sul_ponticello', {})
        position = config.get('cc21_value', 115)
        
        msg = self.mapper.apply_sul_ponticello(position_value=position, time=0)
        return [(0, msg)]
    
    def _apply_sul_tasto(self) -> List[Tuple[int, mido.Message]]:
        """Apply sul tasto articulation from config."""
        config = self.articulation_config.get('sul_tasto', {})
        position = config.get('cc21_value', 15)
        
        msg = self.mapper.apply_sul_tasto(position_value=position, time=0)
        return [(0, msg)]
    
    def _apply_slur(self) -> List[Tuple[int, mido.Message]]:
        """Apply slur/legato articulation from config."""
        config = self.articulation_config.get('slur', {})
        messages = []
        
        # Enable legato (CC64)
        cc64_value = config.get('cc64', 127)
        messages.append((0, mido.Message(
            'control_change',
            channel=self.mapper.channel,
            control=self.mapper.CC_SUSTAIN,
            value=cc64_value,
            time=0
        )))
        
        # Add portamento if configured
        portamento = config.get('cc5_portamento', 0)
        if portamento > 0:
            msg = self.mapper.apply_portamento(amount=portamento, time=0)
            messages.append((0, msg))
        
        return messages
    
    def _apply_accent(self, base_cc11: int) -> List[Tuple[int, mido.Message]]:
        """Apply accent articulation from config."""
        config = self.articulation_config.get('accent', {})
        peak = config.get('cc11_peak', 110)
        
        messages = []
        
        # Spike to peak
        messages.append((0, mido.Message(
            'control_change',
            channel=self.mapper.channel,
            control=self.mapper.CC_EXPRESSION,
            value=peak,
            time=0
        )))
        
        # Return to base after brief spike
        messages.append((10, mido.Message(
            'control_change',
            channel=self.mapper.channel,
            control=self.mapper.CC_EXPRESSION,
            value=base_cc11,
            time=0
        )))
        
        return messages
    
    def _apply_glissando(self) -> List[Tuple[int, mido.Message]]:
        """Apply glissando (pitch slide) from config."""
        config = self.articulation_config.get('glissando', {})
        portamento = config.get('cc5_portamento', 80)
        
        messages = []
        
        # Set high portamento for noticeable pitch slide
        msg = self.mapper.apply_portamento(amount=portamento, time=0)
        messages.append((0, msg))
        
        # Enable legato for smooth glide
        messages.append((0, mido.Message(
            'control_change',
            channel=self.mapper.channel,
            control=self.mapper.CC_SUSTAIN,
            value=127,
            time=0
        )))
        
        return messages
    
    def _apply_crescendo(
        self,
        start_cc11: int,
        duration_ticks: int
    ) -> List[Tuple[int, mido.Message]]:
        """Apply crescendo from config."""
        config = self.articulation_config.get('crescendo', {})
        
        ramp_type = config.get('ramp_type', 'exponential')
        steps = config.get('steps', 15)
        
        # Assume crescendo goes to higher dynamic (add 30 to start)
        end_value = min(127, start_cc11 + 30)
        
        if ramp_type == 'exponential':
            return self.mapper.create_exponential_crescendo(
                start_value=start_cc11,
                end_value=end_value,
                duration_ticks=duration_ticks,
                steps=steps,
                curve=2.0
            )
        else:
            # Linear crescendo (use existing method)
            return self.mapper.create_crescendo(
                start_value=start_cc11,
                end_value=end_value,
                duration_ticks=duration_ticks,
                steps=steps
            )
    
    def _apply_diminuendo(
        self,
        start_cc11: int,
        duration_ticks: int
    ) -> List[Tuple[int, mido.Message]]:
        """Apply diminuendo from config."""
        config = self.articulation_config.get('diminuendo', {})
        
        ramp_type = config.get('ramp_type', 'exponential')
        steps = config.get('steps', 15)
        
        # Assume diminuendo goes to lower dynamic (subtract 30 from start)
        end_value = max(20, start_cc11 - 30)
        
        if ramp_type == 'exponential':
            return self.mapper.create_exponential_crescendo(
                start_value=start_cc11,
                end_value=end_value,
                duration_ticks=duration_ticks,
                steps=steps,
                curve=2.0
            )
        else:
            return self.mapper.create_crescendo(
                start_value=start_cc11,
                end_value=end_value,
                duration_ticks=duration_ticks,
                steps=steps
            )
    
    def get_dynamic_cc_value(self, dynamic_marking: str) -> int:
        """
        Get CC11 value for a dynamic marking (pp, mf, ff, etc.).
        
        Args:
            dynamic_marking: Dynamic marking string (e.g., 'mf', 'ff')
            
        Returns:
            CC11 expression value (0-127)
        """
        return self.dynamics_config.get(dynamic_marking.lower(), 80)
    
    def calculate_note_overlap(
        self,
        note_duration_ticks: int,
        overlap_percent: int = 10
    ) -> int:
        """
        Calculate overlap duration for legato/slur notes.
        
        Args:
            note_duration_ticks: Original note duration in ticks
            overlap_percent: Percentage of next note to overlap
            
        Returns:
            Overlap duration in ticks
        """
        return int(note_duration_ticks * (overlap_percent / 100))
    
    def shorten_note_for_articulation(
        self,
        note_duration_ticks: int,
        articulation_type: ArticulationType
    ) -> int:
        """
        Shorten note duration for articulations like staccato.
        
        Args:
            note_duration_ticks: Original note duration in ticks
            articulation_type: Type of articulation
            
        Returns:
            Shortened duration in ticks
        """
        if articulation_type == ArticulationType.STACCATO:
            config = self.articulation_config.get('staccato', {})
            percent = config.get('note_duration_percent', 50)
            return int(note_duration_ticks * (percent / 100))
        
        elif articulation_type == ArticulationType.STACCATISSIMO:
            # Very short - 25% duration
            return int(note_duration_ticks * 0.25)
        
        elif articulation_type == ArticulationType.SPICCATO:
            config = self.articulation_config.get('spiccato', {})
            percent = config.get('note_duration_percent', 40)
            return int(note_duration_ticks * (percent / 100))
        
        # No shortening for other articulations
        return note_duration_ticks


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load SWAM configuration from JSON file.
    
    Args:
        config_path: Path to swam_config.json (optional)
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "swam_config.json"
    
    with open(config_path, 'r') as f:
        return json.load(f)
