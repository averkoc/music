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
    CC_PORTAMENTO = 5
    CC_BOW_POSITION = 9  # CC9 for strings (sul ponticello, sul tasto)
    CC_EXPRESSION = 11
    CC_GROWL = 18  # CC18 for saxophone growl
    CC_SUSTAIN = 64
    CC_LEGATO = 68  # CC68 for legato switch (some SWAM instruments)
    CC_BRIGHTNESS = 74
    
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
    
    def apply_staccato(
        self,
        base_cc11: int,
        spike_value: int = 105,
        duration_ticks: int = 0
    ) -> List[Tuple[int, mido.Message]]:
        """
        Apply staccato articulation: spike CC11 then immediately drop.
        
        Args:
            base_cc11: Baseline expression value to return to
            spike_value: Peak CC11 value for accent (default 105)
            duration_ticks: Duration of the note in ticks
            
        Returns:
            List of (time, message) tuples for staccato effect
        """
        messages = []
        
        # Spike CC11 at note onset
        messages.append((0, mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_EXPRESSION,
            value=spike_value,
            time=0
        )))
        
        # Immediately drop to 0 after brief attack (5-10 ticks)
        messages.append((5, mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_EXPRESSION,
            value=0,
            time=0
        )))
        
        # Restore baseline for next note
        messages.append((duration_ticks - 5 if duration_ticks > 10 else 5, mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_EXPRESSION,
            value=base_cc11,
            time=0
        )))
        
        return messages
    
    def apply_vibrato_delayed(
        self,
        target_depth: int = 64,
        delay_ticks: int = 240,
        ramp_duration_ticks: int = 144,
        steps: int = 8
    ) -> List[Tuple[int, mido.Message]]:
        """
        Apply vibrato gradually after note onset (vibrato mark).
        
        Args:
            target_depth: Target CC1 vibrato depth (0-127)
            delay_ticks: Wait this many ticks before starting vibrato
            ramp_duration_ticks: Duration of ramp from 0 to target
            steps: Number of interpolation steps
            
        Returns:
            List of (time, message) tuples for delayed vibrato
        """
        messages = []
        
        # Start with no vibrato
        messages.append((0, mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_MODULATION,
            value=0,
            time=0
        )))
        
        # Wait before starting vibrato
        time_offset = delay_ticks
        
        # Gradual ramp up
        step_size = target_depth / steps
        time_step = ramp_duration_ticks // steps
        
        for i in range(1, steps + 1):
            value = int(step_size * i)
            messages.append((time_offset, mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_MODULATION,
                value=value,
                time=0
            )))
            time_offset = time_step
        
        return messages
    
    def apply_sul_ponticello(
        self,
        position_value: int = 115,
        time: int = 0
    ) -> mido.Message:
        """
        Apply sul ponticello (bow near bridge) using CC9.
        
        Args:
            position_value: CC9 value for bow position (110-127 = near bridge)
            time: Delta time for the message
            
        Returns:
            MIDI control change message for bow position
        """
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_BOW_POSITION,
            value=position_value,
            time=time
        )
    
    def apply_sul_tasto(
        self,
        position_value: int = 15,
        time: int = 0
    ) -> mido.Message:
        """
        Apply sul tasto (bow over fingerboard) using CC9.
        
        Args:
            position_value: CC9 value for bow position (0-20 = over fingerboard)
            time: Delta time for the message
            
        Returns:
            MIDI control change message for bow position
        """
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_BOW_POSITION,
            value=position_value,
            time=time
        )
    
    def apply_portamento(
        self,
        amount: int = 40,
        time: int = 0
    ) -> mido.Message:
        """
        Apply portamento (pitch slide) using CC5.
        
        Args:
            amount: CC5 portamento time (0-127)
            time: Delta time for the message
            
        Returns:
            MIDI control change message for portamento
        """
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_PORTAMENTO,
            value=amount,
            time=time
        )
    
    def create_exponential_crescendo(
        self,
        start_value: int,
        end_value: int,
        duration_ticks: int,
        steps: int = 15,
        curve: float = 2.0
    ) -> List[Tuple[int, mido.Message]]:
        """
        Create an exponential crescendo for more natural dynamics.
        
        Args:
            start_value: Starting expression value (0-127)
            end_value: Ending expression value (0-127)
            duration_ticks: Total duration in MIDI ticks
            steps: Number of intermediate CC messages
            curve: Exponential curve factor (>1 for exponential, 1 for linear)
            
        Returns:
            List of (time, message) tuples for the crescendo
        """
        messages = []
        time_step = duration_ticks // steps
        value_range = end_value - start_value
        
        for i in range(steps + 1):
            # Exponential curve: value = start + range * (i/steps)^curve
            normalized = i / steps
            curved = normalized ** curve
            value = int(start_value + (value_range * curved))
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
    
    def apply_growl(
        self,
        growl_amount: int = 80,
        time: int = 0
    ) -> mido.Message:
        """
        Apply growl effect for saxophone using CC18.
        
        Args:
            growl_amount: CC18 value for growl intensity (0-127)
            time: Delta time for the message
            
        Returns:
            MIDI control change message for growl
        """
        if self.instrument != SWAMInstrument.SAXOPHONE:
            # Growl is primarily for saxophone
            pass
        
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_GROWL,
            value=growl_amount,
            time=time
        )
    
    def create_initialization_messages(self, time: int = 0) -> List[mido.Message]:
        """
        Create initialization messages to "wake up" SWAM instrument.
        
        SWAM instruments need stimulus (expression movement) to activate
        their physical modeling engine. This sends a brief ramp-up and
        ramp-down of expression to ensure the instrument is responsive.
        
        Args:
            time: Starting delta time for messages
            
        Returns:
            List of MIDI control change messages for initialization
        """
        messages = []
        
        # Brief expression ramp to wake up the instrument
        # Start at 0, ramp to 40, then back to default
        init_sequence = [
            (time, 0),           # Start silent
            (10, 40),            # Quick rise
            (10, 20),            # Slight fall
            (10, 60),            # Rise to working level
        ]
        
        for delta_time, value in init_sequence:
            messages.append(mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_EXPRESSION,
                value=value,
                time=delta_time
            ))
        
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
