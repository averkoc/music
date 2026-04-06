"""
SWAM CC Mapper

Utilities for mapping MuseScore musical expressions to SWAM instrument CC messages.
Handles velocity, dynamics, articulations, and expression control.
"""

from enum import Enum
from typing import List, Tuple
import mido


class SWAMInstrument(Enum):
    """Supported SWAM instruments."""
    VIOLIN = "violin"
    SAXOPHONE = "saxophone"


class SWAMCCMapper:
    """
    Maps musical expressions to SWAM continuous controller messages.
    
    SWAM instruments are highly expressive and respond to multiple CC messages:
    - CC1: Modulation (vibrato)
    - CC2: Breath (for wind instruments like saxophone)
    - CC11: Expression (dynamic level)
    - CC74: Brightness (tone color)
    """
    
    # MIDI CC numbers
    CC_MODULATION = 1
    CC_BREATH = 2
    CC_EXPRESSION = 11
    CC_BRIGHTNESS = 74
    CC_SUSTAIN = 64
    
    def __init__(self, instrument: SWAMInstrument):
        """
        Initialize mapper for specific SWAM instrument.
        
        Args:
            instrument: SWAM instrument type
        """
        self.instrument = instrument
        self.channel = 0  # Default MIDI channel
    
    def velocity_to_expression(
        self, 
        velocity: int, 
        time: int = 0
    ) -> List[mido.Message]:
        """
        Convert MIDI velocity to SWAM expression CC.
        
        Args:
            velocity: MIDI velocity (0-127)
            time: Delta time for the message
            
        Returns:
            List of MIDI control change messages
        """
        # Map velocity to expression (CC11)
        # SWAM instruments respond well to CC11 for dynamics
        expression_value = self._velocity_to_cc(velocity)
        
        messages = []
        
        # Add expression CC
        messages.append(mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_EXPRESSION,
            value=expression_value,
            time=time
        ))
        
        # For loud notes, add brightness
        if velocity > 100:
            brightness = min(127, int(expression_value * 1.1))
            messages.append(mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_BRIGHTNESS,
                value=brightness,
                time=0
            ))
        
        return messages
    
    def add_vibrato(
        self, 
        depth: int = 64, 
        time: int = 0
    ) -> mido.Message:
        """
        Add vibrato using modulation (CC1).
        
        Args:
            depth: Vibrato depth (0-127)
            time: Delta time for the message
            
        Returns:
            MIDI control change message
        """
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_MODULATION,
            value=depth,
            time=time
        )
    
    def add_breath(
        self, 
        pressure: int = 64, 
        time: int = 0
    ) -> mido.Message:
        """
        Add breath pressure (CC2) for wind instruments.
        
        Particularly important for SWAM Saxophone.
        
        Args:
            pressure: Breath pressure (0-127)
            time: Delta time for the message
            
        Returns:
            MIDI control change message
        """
        if self.instrument != SWAMInstrument.SAXOPHONE:
            # Breath is primarily for wind instruments
            pass
        
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_BREATH,
            value=pressure,
            time=time
        )
    
    def add_legato(
        self, 
        enabled: bool = True, 
        time: int = 0
    ) -> mido.Message:
        """
        Enable/disable legato using sustain pedal (CC64).
        
        Args:
            enabled: True to enable legato, False to disable
            time: Delta time for the message
            
        Returns:
            MIDI control change message
        """
        value = 127 if enabled else 0
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_SUSTAIN,
            value=value,
            time=time
        )
    
    def create_crescendo(
        self,
        start_value: int,
        end_value: int,
        duration_ticks: int,
        steps: int = 10
    ) -> List[Tuple[int, mido.Message]]:
        """
        Create a crescendo (gradual increase in expression).
        
        Args:
            start_value: Starting expression value (0-127)
            end_value: Ending expression value (0-127)
            duration_ticks: Total duration in MIDI ticks
            steps: Number of intermediate CC messages
            
        Returns:
            List of (time, message) tuples for the crescendo
        """
        messages = []
        step_size = (end_value - start_value) / steps
        time_step = duration_ticks // steps
        
        for i in range(steps + 1):
            value = int(start_value + (step_size * i))
            value = max(0, min(127, value))  # Clamp to valid range
            
            msg = mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_EXPRESSION,
                value=value,
                time=0
            )
            messages.append((time_step * i, msg))
        
        return messages
    
    def _velocity_to_cc(self, velocity: int) -> int:
        """
        Convert MIDI velocity to CC value with appropriate curve.
        
        Args:
            velocity: MIDI velocity (0-127)
            
        Returns:
            CC value (0-127)
        """
        # Apply a curve that makes SWAM instruments more expressive
        # SWAM responds better to CC11 values in the 40-110 range
        normalized = velocity / 127.0
        # Slight exponential curve for more natural dynamics
        curved = normalized ** 0.9
        cc_value = int(curved * 127)
        return max(20, min(127, cc_value))  # Keep minimum at 20 for audibility


def get_default_cc_values(instrument: SWAMInstrument) -> dict:
    """
    Get default CC values for a SWAM instrument.
    
    Args:
        instrument: SWAM instrument type
        
    Returns:
        Dictionary of CC numbers to default values
    """
    defaults = {
        SWAMCCMapper.CC_EXPRESSION: 80,
        SWAMCCMapper.CC_MODULATION: 0,  # No vibrato by default
        SWAMCCMapper.CC_BRIGHTNESS: 64,
    }
    
    if instrument == SWAMInstrument.SAXOPHONE:
        defaults[SWAMCCMapper.CC_BREATH] = 64
    
    return defaults
