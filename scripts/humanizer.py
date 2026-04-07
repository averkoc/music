"""
SWAM Humanizer

Adds natural performance variations to MIDI for realistic SWAM playback.
Implements "friction" through timing jitter, velocity variation, and expression fluctuation.
"""

import random
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class HumanizationConfig:
    """Configuration for humanization parameters."""
    timing_jitter_ms: float = 8.0  # ±8ms timing variation
    velocity_variation_percent: float = 7.0  # ±7% velocity randomization
    duration_variation_percent: float = 2.0  # ±2% duration randomization
    expression_flutter: int = 4  # ±4 CC11 value variation
    bow_detach_variation_ms: float = 5.0  # ±5ms bow lift timing
    seed: int = None  # Random seed for reproducibility (None = random)
    
    def __post_init__(self):
        """Initialize random seed if provided."""
        if self.seed is not None:
            random.seed(self.seed)


class SWAMHumanizer:
    """
    Adds humanization to SWAM MIDI for natural, realistic performance.
    
    Key humanization strategies:
    1. Timing Jitter: Shifts notes slightly off-grid (5-10ms)
    2. Velocity Variation: Randomizes attack strength (±5-10%)
    3. Duration Variation: Adds natural bow detachment (1-3%)
    4. Expression Flutter: Simulates bow pressure fluctuation (CC11 ±3-5)
    """
    
    def __init__(self, config: HumanizationConfig = None):
        """
        Initialize humanizer with configuration.
        
        Args:
            config: HumanizationConfig object (uses defaults if None)
        """
        self.config = config or HumanizationConfig()
    
    def humanize_timing(
        self,
        onset_time_ticks: int,
        ticks_per_beat: int,
        tempo_bpm: int = 120
    ) -> int:
        """
        Add subtle timing jitter to note onset for human imprecision.
        
        Args:
            onset_time_ticks: Original note onset time in ticks
            ticks_per_beat: MIDI ticks per quarter note
            tempo_bpm: Tempo in beats per minute
            
        Returns:
            Adjusted onset time with jitter
        """
        # Calculate ticks per millisecond
        ms_per_beat = 60000 / tempo_bpm
        ticks_per_ms = ticks_per_beat / ms_per_beat
        
        # Apply jitter (±timing_jitter_ms)
        jitter_ms = random.uniform(
            -self.config.timing_jitter_ms,
            self.config.timing_jitter_ms
        )
        jitter_ticks = int(jitter_ms * ticks_per_ms)
        
        return max(0, onset_time_ticks + jitter_ticks)
    
    def humanize_velocity(self, velocity: int) -> int:
        """
        Add variation to velocity for natural attack strength differences.
        
        Args:
            velocity: Original MIDI velocity
            
        Returns:
            Adjusted velocity with variation
        """
        variation_percent = random.uniform(
            -self.config.velocity_variation_percent,
            self.config.velocity_variation_percent
        )
        
        adjusted = velocity * (1 + variation_percent / 100)
        return max(1, min(127, int(adjusted)))
    
    def humanize_duration(self, duration_ticks: int) -> int:
        """
        Add variation to note duration for natural bow detachment.
        
        Args:
            duration_ticks: Original note duration in ticks
            
        Returns:
            Adjusted duration with variation
        """
        variation_percent = random.uniform(
            -self.config.duration_variation_percent,
            self.config.duration_variation_percent
        )
        
        adjusted = duration_ticks * (1 + variation_percent / 100)
        return max(10, int(adjusted))  # Minimum 10 ticks
    
    def humanize_expression(self, cc11_value: int) -> int:
        """
        Add subtle flutter to CC11 expression for bow pressure variation.
        
        Args:
            cc11_value: Original CC11 expression value
            
        Returns:
            Adjusted expression with flutter
        """
        flutter = random.randint(
            -self.config.expression_flutter,
            self.config.expression_flutter
        )
        
        return max(0, min(127, cc11_value + flutter))
    
    def humanize_bow_detachment(
        self,
        gap_ticks: int,
        ticks_per_beat: int,
        tempo_bpm: int = 120
    ) -> int:
        """
        Add variation to gap between notes for natural bow lift timing.
        
        Args:
            gap_ticks: Original gap between note-off and next note-on
            ticks_per_beat: MIDI ticks per quarter note
            tempo_bpm: Tempo in beats per minute
            
        Returns:
            Adjusted gap with variation
        """
        # Calculate ticks per millisecond
        ms_per_beat = 60000 / tempo_bpm
        ticks_per_ms = ticks_per_beat / ms_per_beat
        
        # Apply variation (±bow_detach_variation_ms)
        variation_ms = random.uniform(
            -self.config.bow_detach_variation_ms,
            self.config.bow_detach_variation_ms
        )
        variation_ticks = int(variation_ms * ticks_per_ms)
        
        return max(0, gap_ticks + variation_ticks)
    
    def should_add_expression_flutter(self, probability: float = 0.3) -> bool:
        """
        Randomly decide whether to add expression flutter to a note.
        
        Args:
            probability: Chance of adding flutter (0.0-1.0)
            
        Returns:
            True if flutter should be added
        """
        return random.random() < probability
    
    def get_progressive_fatigue_factor(
        self,
        note_index: int,
        total_notes: int,
        max_fatigue: float = 0.15
    ) -> float:
        """
        Calculate progressive fatigue factor for later notes in performance.
        Simulates human fatigue causing slightly more variation over time.
        
        Args:
            note_index: Current note position (0-based)
            total_notes: Total number of notes in piece
            max_fatigue: Maximum additional variation factor
            
        Returns:
            Fatigue multiplier (1.0 = no fatigue, 1.15 = 15% more variation)
        """
        if total_notes <= 1:
            return 1.0
        
        # Linear fatigue curve
        progress = note_index / total_notes
        fatigue = 1.0 + (progress * max_fatigue)
        
        return fatigue


def create_default_humanizer() -> SWAMHumanizer:
    """Create a humanizer with default configuration."""
    return SWAMHumanizer()


def create_subtle_humanizer() -> SWAMHumanizer:
    """Create a humanizer with subtle, conservative settings."""
    config = HumanizationConfig(
        timing_jitter_ms=5.0,
        velocity_variation_percent=4.0,
        duration_variation_percent=1.5,
        expression_flutter=2,
        bow_detach_variation_ms=3.0
    )
    return SWAMHumanizer(config)


def create_aggressive_humanizer() -> SWAMHumanizer:
    """Create a humanizer with more obvious variation."""
    config = HumanizationConfig(
        timing_jitter_ms=12.0,
        velocity_variation_percent=10.0,
        duration_variation_percent=3.5,
        expression_flutter=6,
        bow_detach_variation_ms=8.0
    )
    return SWAMHumanizer(config)
