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
    CC_EXPRESSION = 11
    CC_VIBRATO_RATE = 17  # CC17 for vibrato speed
    CC_GROWL = 18  # CC18 for saxophone growl
    CC_TREMOLO = 19  # CC19 for tremolo (OFF=0, SLOW=64, FAST=127)
    CC_BOW_FORCE = 20  # CC20 for bow pressure on strings
    CC_BOW_POSITION = 21  # CC21 for bow position (sul tasto to sul ponticello)
    CC_SUSTAIN = 64
    CC_LEGATO = 68  # CC68 for legato switch (some SWAM instruments)
    CC_HARMONICS = 74  # Custom mapping - adds harmonic content/brilliance
    
    def __init__(self, instrument: SWAMInstrument):
        """
        Initialize mapper for specific SWAM instrument.
        
        Args:
            instrument: SWAM instrument type
        """
        self.instrument = instrument
        self.channel = 0  # Default MIDI channel
    
    def _cc11_to_cc2(self, cc11_value: int) -> int:
        """
        Calculate CC2 (Bow Pressure/Breath) from CC11 (Expression).
        
        Couples bow pressure to dynamics for realistic performance:
        - Soft playing (low CC11) = light bow pressure (lower CC2)
        - Loud playing (high CC11) = heavy bow pressure (higher CC2)
        
        Args:
            cc11_value: CC11 expression value (0-127)
            
        Returns:
            CC2 bow pressure value (0-127)
        """
        # CC2 follows CC11 with slight offset to avoid over-saturation
        # Formula: CC2 = CC11 * 0.85 + 10 (keeps CC2 in sweet spot)
        cc2_value = int(cc11_value * 0.85 + 10)
        return max(20, min(127, cc2_value))  # Clamp to valid range
    
    def _create_ramp(
        self,
        cc_number: int,
        start_value: int,
        end_value: int,
        duration_ticks: int,
        steps: int = 3
    ) -> List[Tuple[int, mido.Message]]:
        """
        Create a smooth ramp between two CC values for human-like transitions.
        
        Args:
            cc_number: MIDI CC number to ramp
            start_value: Starting CC value
            end_value: Target CC value
            duration_ticks: Duration of ramp in ticks
            steps: Number of interpolation steps (default 3 for subtle smoothing)
            
        Returns:
            List of (time_offset, message) tuples
        """
        messages = []
        
        if steps <= 1:
            # No interpolation, just immediate change
            messages.append((0, mido.Message(
                'control_change',
                channel=self.channel,
                control=cc_number,
                value=end_value,
                time=0
            )))
            return messages
        
        # Calculate step size for time and value
        time_step = duration_ticks // steps
        value_diff = end_value - start_value
        
        for i in range(steps):
            # Linear interpolation
            progress = (i + 1) / steps
            interpolated_value = int(start_value + (value_diff * progress))
            time_offset = time_step * i
            
            messages.append((time_offset, mido.Message(
                'control_change',
                channel=self.channel,
                control=cc_number,
                value=interpolated_value,
                time=0
            )))
        
        return messages
    
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
            harmonics = min(127, int(expression_value * 1.1))
            messages.append(mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_HARMONICS,
                value=harmonics,
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
            depth: Vibrato depth (0-110, SWAM maximum is 110)
            time: Delta time for the message
            
        Returns:
            MIDI control change message
        """
        # Clamp to SWAM's maximum vibrato depth of 110
        clamped_depth = max(0, min(110, depth))
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_MODULATION,
            value=clamped_depth,
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
        Apply staccato articulation: ramp up to spike then decay with sustain.
        
        Args:
            base_cc11: Baseline expression value to return to
            spike_value: Peak CC11 value for accent (default 105)
            duration_ticks: Duration of the note in ticks
            
        Returns:
            List of (time, message) tuples for staccato effect
        """
        messages = []
        
        # Quick ramp up to spike (2 steps over 2 ticks for natural attack)
        ramp_up = self._create_ramp(
            cc_number=self.CC_EXPRESSION,
            start_value=base_cc11,
            end_value=spike_value,
            duration_ticks=2,
            steps=2
        )
        for time_offset, cc11_msg in ramp_up:
            messages.append((time_offset, cc11_msg))
            # Add coupled CC2 (bow pressure)
            cc2_value = self._cc11_to_cc2(cc11_msg.value)
            cc2_msg = mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_BREATH,
                value=cc2_value,
                time=0
            )
            messages.append((time_offset, cc2_msg))
        
        # Quick decay to sustain level (3 steps over 4 ticks)
        sustain_level = max(20, int(base_cc11 * 0.4))
        ramp_down = self._create_ramp(
            cc_number=self.CC_EXPRESSION,
            start_value=spike_value,
            end_value=sustain_level,
            duration_ticks=4,
            steps=3
        )
        # Offset by the ramp up duration
        for time_offset, cc11_msg in ramp_down:
            messages.append((time_offset + 2, cc11_msg))
            # Add coupled CC2
            cc2_value = self._cc11_to_cc2(cc11_msg.value)
            cc2_msg = mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_BREATH,
                value=cc2_value,
                time=0
            )
            messages.append((time_offset + 2, cc2_msg))
        
        # Restore baseline for next note (gradual)
        restore_time = duration_ticks - 6 if duration_ticks > 10 else 5
        messages.append((restore_time, mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_EXPRESSION,
            value=base_cc11,
            time=0
        )))
        
        return messages
    
    def apply_accent(
        self,
        base_cc11: int,
        peak_value: int = 110,
        sustain_value: int = None
    ) -> List[Tuple[int, mido.Message]]:
        """
        Apply accent articulation: smooth ramp to peak then decay to sustain.
        
        Args:
            base_cc11: Baseline expression value
            peak_value: Peak CC11 value for accent (default 110)
            sustain_value: Sustained level after attack (defaults to base_cc11)
            
        Returns:
            List of (time, message) tuples for accent effect
        """
        messages = []
        sustain = sustain_value if sustain_value is not None else base_cc11
        
        # Smooth ramp up to peak (3 steps over 6 ticks)
        ramp_up = self._create_ramp(
            cc_number=self.CC_EXPRESSION,
            start_value=base_cc11,
            end_value=peak_value,
            duration_ticks=6,
            steps=3
        )
        for time_offset, cc11_msg in ramp_up:
            messages.append((time_offset, cc11_msg))
            # Add coupled CC2
            cc2_value = self._cc11_to_cc2(cc11_msg.value)
            cc2_msg = mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_BREATH,
                value=cc2_value,
                time=0
            )
            messages.append((time_offset, cc2_msg))
        
        # Quick decay to sustained level (2 steps over 4 ticks)
        ramp_down = self._create_ramp(
            cc_number=self.CC_EXPRESSION,
            start_value=peak_value,
            end_value=sustain,
            duration_ticks=4,
            steps=2
        )
        for time_offset, cc11_msg in ramp_down:
            messages.append((time_offset + 6, cc11_msg))
            # Add coupled CC2
            cc2_value = self._cc11_to_cc2(cc11_msg.value)
            cc2_msg = mido.Message(
                'control_change',
                channel=self.channel,
                control=self.CC_BREATH,
                value=cc2_value,
                time=0
            )
            messages.append((time_offset + 6, cc2_msg))
        
        return messages
    
    def apply_marcato(
        self,
        base_cc11: int,
        peak_value: int = 120,
        sustain_value: int = None
    ) -> List[Tuple[int, mido.Message]]:
        """
        Apply marcato articulation: strong ramp to peak then decay to sustain.
        
        Args:
            base_cc11: Baseline expression value
            peak_value: Peak CC11 value for marcato (default 120)
            sustain_value: Sustained level after attack (defaults to base_cc11)
            
        Returns:
            List of (time, message) tuples for marcato effect
        """
        messages = []
        sustain = sustain_value if sustain_value is not None else base_cc11
        
        # Strong ramp up to very high peak (4 steps over 8 ticks)
        ramp_up = self._create_ramp(
            cc_number=self.CC_EXPRESSION,
            start_value=base_cc11,
            end_value=peak_value,
            duration_ticks=8,
            steps=4
        )
        # Add CC11 messages with coupled CC2 (bow pressure)
        for time_offset, cc11_msg in ramp_up:
            messages.append((time_offset, cc11_msg))
            cc2_value = self._cc11_to_cc2(cc11_msg.value)
            cc2_msg = mido.Message('control_change', channel=self.channel,
                                   control=self.CC_BREATH, value=cc2_value, time=0)
            messages.append((time_offset, cc2_msg))
        
        # Slightly longer decay (3 steps over 7 ticks)
        ramp_down = self._create_ramp(
            cc_number=self.CC_EXPRESSION,
            start_value=peak_value,
            end_value=sustain,
            duration_ticks=7,
            steps=3
        )
        # Add CC11 messages with coupled CC2 (bow pressure)
        for time_offset, cc11_msg in ramp_down:
            messages.append((time_offset + 8, cc11_msg))
            cc2_value = self._cc11_to_cc2(cc11_msg.value)
            cc2_msg = mido.Message('control_change', channel=self.channel,
                                   control=self.CC_BREATH, value=cc2_value, time=0)
            messages.append((time_offset + 8, cc2_msg))
        
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
            target_depth: Target CC1 vibrato depth (0-110, SWAM maximum is 110)
            delay_ticks: Wait this many ticks before starting vibrato
            ramp_duration_ticks: Duration of ramp from 0 to target
            steps: Number of interpolation steps (recommend 8-12 for smoothness)
            
        Returns:
            List of (time, message) tuples for delayed vibrato
        """
        messages = []
                # Clamp target_depth to SWAM's maximum of 110
        target_depth = min(110, target_depth)
                # Start with no vibrato
        messages.append((0, mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_MODULATION,
            value=0,
            time=0
        )))
        
        # Use the ramp generator for smooth vibrato onset
        ramp = self._create_ramp(
            cc_number=self.CC_MODULATION,
            start_value=0,
            end_value=target_depth,
            duration_ticks=ramp_duration_ticks,
            steps=max(8, steps)  # Ensure at least 8 steps for smoothness
        )
        
        # Add delay offset to all ramp messages
        for ramp_offset, msg in ramp:
            messages.append((delay_ticks + ramp_offset if ramp_offset == 0 else ramp_offset, msg))
        
        return messages
    
    def create_note_envelope(
        self,
        envelope_type: str,
        base_cc11: int,
        duration_ticks: int,
        velocity: int = 64
    ) -> List[Tuple[int, mido.Message]]:
        """
        Create a CC11 envelope for a note to add natural bow/breath dynamics.
        
        This is THE critical feature for realistic SWAM - every note needs dynamic
        shaping, not flat CC11. Different envelope types create different articulations.
        
        Args:
            envelope_type: Type of envelope ('default', 'expressive', 'gentle', 'percussive')
            base_cc11: Baseline expression value (0-127)
            duration_ticks: Total duration of the note in ticks
            velocity: Note velocity for dynamic scaling (0-127)
            
        Returns:
            List of (time_offset, message) tuples for the envelope
        """
        messages = []
        
        # Scale envelope based on velocity
        velocity_scale = velocity / 127.0
        
        # Define envelope shapes as (time_ratio, cc11_ratio) points
        # time_ratio: position in note (0.0 = start, 1.0 = end)
        # cc11_ratio: expression relative to base (1.0 = base, 1.2 = 20% above)
        envelopes = {
            'default': [
                (0.0, 0.7),   # Start softer
                (0.15, 1.0),  # Rise to base
                (0.7, 1.0),   # Sustain
                (1.0, 0.85),  # Gentle release
            ],
            'expressive': [
                (0.0, 0.6),   # Soft start
                (0.2, 1.1),   # Rise above base
                (0.5, 1.05),  # Slight decay
                (0.8, 1.0),   # Return to base
                (1.0, 0.8),   # Clear release
            ],
            'gentle': [
                (0.0, 0.75),  # Gentle attack
                (0.25, 0.95), # Gradual rise
                (0.8, 0.9),   # Sustained
                (1.0, 0.7),   # Soft release
            ],
            'percussive': [
                (0.0, 0.8),   # Quick start
                (0.08, 1.15), # Sharp peak
                (0.2, 0.85),  # Fast decay
                (0.6, 0.75),  # Low sustain
                (1.0, 0.6),   # Release
            ]
        }
        
        envelope_points = envelopes.get(envelope_type, envelopes['default'])
        
        # Generate CC messages from envelope points
        for i in range(len(envelope_points)):
            time_ratio, cc11_ratio = envelope_points[i]
            
            # Calculate absolute values
            time_offset = int(duration_ticks * time_ratio)
            cc11_value = int(base_cc11 * cc11_ratio * (0.7 + 0.3 * velocity_scale))
            cc11_value = max(20, min(127, cc11_value))  # Clamp to valid range
            
            # Create smooth interpolation to next point if not the last
            if i < len(envelope_points) - 1:
                next_time_ratio, next_cc11_ratio = envelope_points[i + 1]
                next_time_offset = int(duration_ticks * next_time_ratio)
                next_cc11_value = int(base_cc11 * next_cc11_ratio * (0.7 + 0.3 * velocity_scale))
                next_cc11_value = max(20, min(127, next_cc11_value))
                
                # Create smooth ramp between points
                segment_duration = next_time_offset - time_offset
                steps = max(2, segment_duration // 40)  # One step per ~40 ticks
                
                ramp = self._create_ramp(
                    cc_number=self.CC_EXPRESSION,
                    start_value=cc11_value,
                    end_value=next_cc11_value,
                    duration_ticks=segment_duration,
                    steps=steps
                )
                
                # Add CC11 messages with coupled CC2 (bow pressure)
                for ramp_offset, cc11_msg in ramp:
                    # Add CC11 message
                    messages.append((time_offset + ramp_offset, cc11_msg))
                    
                    # Add CC2 (bow pressure) message coupled to CC11
                    cc2_value = self._cc11_to_cc2(cc11_msg.value)
                    cc2_msg = mido.Message(
                        'control_change',
                        channel=self.channel,
                        control=self.CC_BREATH,
                        value=cc2_value,
                        time=0
                    )
                    messages.append((time_offset + ramp_offset, cc2_msg))
        
        return messages
    
    def calculate_portamento_amount(
        self,
        prev_pitch: int,
        current_pitch: int,
        base_amount: int = 50
    ) -> int:
        """
        Calculate interval-aware portamento amount (CC70 or CC5).
        
        This adds musical intelligence - small intervals get subtle slides,
        large leaps get more pronounced portamento based on musical context.
        
        Args:
            prev_pitch: Previous MIDI note number (0-127)
            current_pitch: Current MIDI note number (0-127)
            base_amount: Base portamento intensity (0-127)
            
        Returns:
            CC value for portamento (0-127)
        """
        if prev_pitch is None:
            return 0  # No portamento for first note
        
        # Calculate interval in semitones
        interval = abs(current_pitch - prev_pitch)
        
        # Musical interval-based portamento mapping
        if interval == 0:
            # Same note (repeated) - no slide
            return 0
        elif interval == 1:
            # Half-step - very subtle slide
            return int(base_amount * 0.1)
        elif interval == 2:
            # Whole-step - subtle slide
            return int(base_amount * 0.2)
        elif interval <= 4:
            # Minor/major third - moderate slide
            return int(base_amount * 0.35)
        elif interval <= 7:
            # Fourth/fifth - noticeable slide
            return int(base_amount * 0.5)
        elif interval <= 12:
            # Octave or less - expressive slide
            return int(base_amount * 0.7)
        else:
            # Large leap - maximum expressiveness
            return int(base_amount * 0.9)
    
    def apply_portamento_smart(
        self,
        prev_pitch: int,
        current_pitch: int,
        base_amount: int = 60,
        time: int = 0
    ) -> mido.Message:
        """
        Apply interval-aware portamento using CC5.
        
        Args:
            prev_pitch: Previous MIDI note number
            current_pitch: Current MIDI note number
            base_amount: Base portamento intensity (0-127)
            time: Delta time for the message
            
        Returns:
            MIDI control change message for portamento
        """
        amount = self.calculate_portamento_amount(prev_pitch, current_pitch, base_amount)
        
        return mido.Message(
            'control_change',
            channel=self.channel,
            control=self.CC_PORTAMENTO,
            value=amount,
            time=time
        )
    
    def apply_sul_ponticello(
        self,
        position_value: int = 115,
        time: int = 0
    ) -> mido.Message:
        """
        Apply sul ponticello (bow near bridge) using CC21.
        
        Args:
            position_value: CC21 value for bow position (110-127 = near bridge)
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
        Apply sul tasto (bow over fingerboard) using CC21.
        
        Args:
            position_value: CC21 value for bow position (0-20 = over fingerboard)
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
            amount: CC5 portamento time (0=off, 1-127 active; SWAM minimum when active is 1)
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
        SWAMCCMapper.CC_HARMONICS: 64,
    }
    
    if instrument == SWAMInstrument.SAXOPHONE:
        defaults[SWAMCCMapper.CC_BREATH] = 64
    
    return defaults
