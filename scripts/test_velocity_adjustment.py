"""
Test script to demonstrate velocity adjustments for articulations.

This shows how different articulations modify note velocity values.
"""

from swam_cc_mapper import SWAMInstrument
from articulation_mapper import ArticulationMapper
from articulation_detector import ArticulationType


def test_velocity_adjustments():
    """Test velocity adjustments for different instruments and articulations."""
    
    instruments = [SWAMInstrument.VIOLIN, SWAMInstrument.SAXOPHONE]
    articulations = [
        ArticulationType.STACCATO,
        ArticulationType.ACCENT,
        ArticulationType.MARCATO,
        ArticulationType.LEGATO,
        ArticulationType.SLUR
    ]
    base_velocities = [60, 80, 100]
    
    for instrument in instruments:
        print(f"\n{'='*60}")
        print(f"{instrument.value.upper()} - Velocity Adjustments")
        print(f"{'='*60}")
        
        mapper = ArticulationMapper(instrument)
        
        for articulation in articulations:
            print(f"\n{articulation.value}:")
            print(f"  {'Base Velocity':<15} -> {'Adjusted Velocity':<18} (Boost)")
            print(f"  {'-'*50}")
            
            for base_vel in base_velocities:
                adjusted = mapper.get_velocity_adjustment(articulation, base_vel)
                boost = adjusted - base_vel
                print(f"  {base_vel:<15} -> {adjusted:<18} (+{boost})")


if __name__ == "__main__":
    test_velocity_adjustments()
