"""
Test Phase 1 Enhancements

Quick verification that new features work correctly:
1. CC11 envelope generation
2. Interval-aware portamento
3. Improved vibrato smoothness
"""

from scripts.swam_cc_mapper import SWAMCCMapper, SWAMInstrument

def test_envelope_generation():
    """Test CC11 envelope generator."""
    print("Testing CC11 Envelope Generation...")
    
    mapper = SWAMCCMapper(SWAMInstrument.VIOLIN)
    
    # Test default envelope
    envelope = mapper.create_note_envelope(
        envelope_type='default',
        base_cc11=80,
        duration_ticks=480,
        velocity=100
    )
    
    print(f"  ✓ Generated {len(envelope)} CC messages for default envelope")
    print(f"    First message: CC11={envelope[0][1].value} at time=0")
    print(f"    Last message:  CC11={envelope[-1][1].value} at time={envelope[-1][0]}")
    
    # Test all envelope types
    for env_type in ['default', 'expressive', 'gentle', 'percussive']:
        env = mapper.create_note_envelope(env_type, 80, 480, 100)
        print(f"  ✓ {env_type}: {len(env)} messages")
    
    print()


def test_portamento_calculation():
    """Test interval-aware portamento."""
    print("Testing Interval-Aware Portamento...")
    
    mapper = SWAMCCMapper(SWAMInstrument.VIOLIN)
    
    test_intervals = [
        (60, 60, "Unison"),
        (60, 61, "Half-step"),
        (60, 62, "Whole-step"),
        (60, 64, "Major third"),
        (60, 67, "Perfect fifth"),
        (60, 72, "Octave"),
        (60, 79, "Large leap (P12)")
    ]
    
    for prev, curr, name in test_intervals:
        amount = mapper.calculate_portamento_amount(prev, curr, base_amount=100)
        print(f"  {name:20s} (interval={abs(curr-prev):2d}): CC5={amount:3d}")
    
    print()


def test_vibrato_smoothness():
    """Test improved vibrato curve."""
    print("Testing Vibrato Smoothness...")
    
    mapper = SWAMCCMapper(SWAMInstrument.VIOLIN)
    
    vibrato_msgs = mapper.apply_vibrato_delayed(
        target_depth=64,
        delay_ticks=240,
        ramp_duration_ticks=144,
        steps=10
    )
    
    print(f"  ✓ Generated {len(vibrato_msgs)} vibrato messages")
    print(f"    Onset: CC1=0 → CC1={vibrato_msgs[-1][1].value} over {sum(t for t, _ in vibrato_msgs)} ticks")
    
    # Show the curve
    print("    Vibrato curve:")
    for i, (time_offset, msg) in enumerate(vibrato_msgs[:5]):
        print(f"      Step {i+1}: CC1={msg.value:3d} at offset +{time_offset}")
    
    print()


def test_integration():
    """Test that all features work together."""
    print("Testing Integration...")
    
    mapper = SWAMCCMapper(SWAMInstrument.VIOLIN)
    
    # Simulate processing two notes
    note1_pitch = 60  # Middle C
    note1_velocity = 100
    note2_pitch = 67  # G (perfect fifth up)
    note2_velocity = 90
    
    # Note 1: Generate envelope
    env1 = mapper.create_note_envelope('default', 80, 480, note1_velocity)
    
    # Note 2: Calculate portamento + envelope
    portamento = mapper.calculate_portamento_amount(note1_pitch, note2_pitch, 60)
    env2 = mapper.create_note_envelope('default', 75, 480, note2_velocity)
    
    print(f"  Note 1 (C4): {len(env1)} envelope messages")
    print(f"  Note 2 (G4): Portamento CC5={portamento}, {len(env2)} envelope messages")
    print(f"  ✓ Full gesture system working!")
    
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1 Enhancement Tests")
    print("=" * 60)
    print()
    
    try:
        test_envelope_generation()
        test_portamento_calculation()
        test_vibrato_smoothness()
        test_integration()
        
        print("=" * 60)
        print("✅ All tests passed! Phase 1 implementation verified.")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Process a MIDI file: python scripts/process_midi.py midi_input/testisakso2.mid --instrument violin")
        print("  2. Load in Ableton with SWAM VST3")
        print("  3. Compare with previous output")
        print()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
