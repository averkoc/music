"""
Example: Using Articulation Mapper

Demonstrates how to apply articulations to MIDI using the new
configurable articulation system.
"""

from pathlib import Path
from swam_cc_mapper import SWAMInstrument
from articulation_mapper import ArticulationMapper
from articulation_detector import ArticulationType
import mido


def example_apply_articulations():
    """
    Example: Apply various articulations to a simple melody.
    """
    # Create mapper for violin
    mapper = ArticulationMapper(SWAMInstrument.VIOLIN)
    
    # Base dynamic (mf)
    base_cc11 = mapper.get_dynamic_cc_value('mf')  # Returns 80
    
    print(f"Base CC11 for 'mf' dynamic: {base_cc11}")
    print("\n" + "="*60)
    
    # ===== STACCATO =====
    print("\n1. STACCATO Articulation:")
    print("   - Spike CC11 then drop immediately")
    print("   - Shorten note duration to 50%")
    
    note_duration = 480  # Quarter note at 480 ticks per beat
    staccato_msgs = mapper.apply_articulation(
        ArticulationType.STACCATO,
        base_cc11=base_cc11,
        note_duration_ticks=note_duration,
        tempo_bpm=120
    )
    
    shortened_duration = mapper.shorten_note_for_articulation(
        note_duration,
        ArticulationType.STACCATO
    )
    
    print(f"   Original duration: {note_duration} ticks")
    print(f"   Shortened to: {shortened_duration} ticks")
    print(f"   CC messages: {len(staccato_msgs)}")
    for time_offset, msg in staccato_msgs:
        print(f"      @{time_offset} ticks: CC{msg.control} = {msg.value}")
    
    # ===== VIBRATO =====
    print("\n2. VIBRATO Articulation:")
    print("   - Wait 500ms after note onset")
    print("   - Gradually ramp CC1 to target depth")
    
    vibrato_msgs = mapper.apply_articulation(
        ArticulationType.VIBRATO,
        base_cc11=base_cc11,
        note_duration_ticks=note_duration,
        tempo_bpm=120
    )
    
    print(f"   CC messages: {len(vibrato_msgs)}")
    print(f"   First message: @{vibrato_msgs[0][0]} ticks (delay)")
    print(f"   Target CC1 value: {vibrato_msgs[-1][1].value}")
    
    # ===== SUL PONTICELLO =====
    print("\n3. SUL PONTICELLO Articulation:")
    print("   - Set CC9 (bow position) near bridge")
    
    sul_pont_msgs = mapper.apply_articulation(
        ArticulationType.SUL_PONTICELLO,
        base_cc11=base_cc11,
        note_duration_ticks=note_duration,
        tempo_bpm=120
    )
    
    for time_offset, msg in sul_pont_msgs:
        print(f"   CC{msg.control} = {msg.value} (bright, metallic tone)")
    
    # ===== SLUR / LEGATO =====
    print("\n4. SLUR Articulation:")
    print("   - Enable CC64 (sustain/legato)")
    print("   - Add CC5 (portamento) for pitch slide")
    
    slur_msgs = mapper.apply_articulation(
        ArticulationType.SLUR,
        base_cc11=base_cc11,
        note_duration_ticks=note_duration,
        tempo_bpm=120
    )
    
    overlap = mapper.calculate_note_overlap(note_duration, overlap_percent=15)
    print(f"   Overlap next note by: {overlap} ticks (15%)")
    print(f"   CC messages:")
    for time_offset, msg in slur_msgs:
        print(f"      CC{msg.control} = {msg.value}")
    
    # ===== CRESCENDO =====
    print("\n5. CRESCENDO Articulation:")
    print("   - Exponential ramp of CC11")
    print("   - More natural than linear")
    
    crescendo_msgs = mapper.apply_articulation(
        ArticulationType.CRESCENDO,
        base_cc11=base_cc11,
        note_duration_ticks=note_duration * 4,  # Over 4 beats
        tempo_bpm=120
    )
    
    print(f"   CC messages: {len(crescendo_msgs)} steps")
    print(f"   Start value: {crescendo_msgs[0][1].value}")
    print(f"   End value: {crescendo_msgs[-1][1].value}")
    print(f"   Curve type: exponential")
    
    print("\n" + "="*60)
    print("\nConfiguration is loaded from: config/swam_config.json")
    print("All values are customizable per instrument (violin, saxophone)")


def example_customize_config():
    """
    Example: Show how to customize articulation settings.
    """
    print("\n\nCUSTOMIZING ARTICULATIONS")
    print("="*60)
    
    print("""
To customize articulation behavior, edit config/swam_config.json:

1. STACCATO:
   {
     "note_duration_percent": 50,    // 50% of written duration
     "cc11_spike": 105,               // Peak expression value
     "cc11_base_offset": 0            // Offset from base dynamic
   }

2. VIBRATO:
   {
     "cc1_target": 64,                // Moderate vibrato depth
     "delay_ms": 500,                 // Wait 500ms before vibrato
     "ramp_duration_ms": 300          // Smooth 300ms ramp
   }

3. SUL PONTICELLO:
   {
     "cc9_value": 115,                // Default bow position
     "cc9_range": [110, 127]          // Valid range for effect
   }

4. CRESCENDO/DIMINUENDO:
   {
     "cc": 11,                        // Use CC11 (expression)
     "ramp_type": "exponential",      // "exponential" or "linear"
     "steps": 15                      // Number of CC messages
   }

Each instrument (violin, saxophone) has its own articulation settings!
    """)


if __name__ == "__main__":
    example_apply_articulations()
    example_customize_config()
