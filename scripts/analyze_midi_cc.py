#!/usr/bin/env python3
"""
Quick MIDI CC diagnostic tool
Analyzes MIDI files to show what CC messages are present
"""

import sys
from pathlib import Path
import mido

def analyze_midi_file(filepath):
    """Analyze a MIDI file and report all CC messages"""
    print(f"\n{'='*60}")
    print(f"📁 Analyzing: {filepath.name}")
    print(f"{'='*60}\n")
    
    try:
        mid = mido.MidiFile(filepath)
    except Exception as e:
        print(f"❌ Error loading MIDI file: {e}")
        return
    
    print(f"Format: Type {mid.type}")
    print(f"Ticks per beat: {mid.ticks_per_beat}")
    print(f"Number of tracks: {len(mid.tracks)}\n")
    
    # Collect all messages
    all_messages = []
    for track in mid.tracks:
        all_messages.extend(track)
    
    # Count message types
    msg_types = {}
    cc_messages = []
    note_messages = []
    pitchwheel_messages = []
    
    for msg in all_messages:
        msg_type = msg.type
        msg_types[msg_type] = msg_types.get(msg_type, 0) + 1
        
        if msg_type == 'control_change':
            cc_messages.append(msg)
        elif msg_type in ('note_on', 'note_off'):
            note_messages.append(msg)
        elif msg_type == 'pitchwheel':
            pitchwheel_messages.append(msg)
    
    print("📊 Message Type Breakdown:")
    for msg_type, count in sorted(msg_types.items()):
        print(f"   {msg_type:20} {count:5}")
    
    # Analyze CC messages
    print(f"\n🎛️  Control Change (CC) Analysis:")
    print(f"   Total CC messages: {len(cc_messages)}")
    
    if len(cc_messages) == 0:
        print("   ❌ NO CC MESSAGES FOUND!")
        print("   This file has no expression/dynamics data for SWAM.")
    else:
        # Group by CC number
        cc_by_number = {}
        for msg in cc_messages:
            cc_num = msg.control
            if cc_num not in cc_by_number:
                cc_by_number[cc_num] = []
            cc_by_number[cc_num].append(msg)
        
        print(f"\n   CC Numbers present: {sorted(cc_by_number.keys())}")
        print(f"\n   Breakdown by CC number:")
        
        cc_names = {
            1: 'Modulation', 2: 'Breath', 4: 'Foot', 5: 'Portamento Time',
            7: 'Volume', 10: 'Pan', 11: 'Expression', 17: 'CC17', 20: 'CC20',
            21: 'CC21', 64: 'Sustain', 65: 'Portamento', 66: 'Sostenuto',
            67: 'Soft Pedal', 68: 'Legato', 71: 'Resonance', 72: 'Release',
            73: 'Attack', 74: 'Brightness', 84: 'Portamento Ctrl',
            91: 'Reverb', 93: 'Chorus'
        }
        
        for cc_num in sorted(cc_by_number.keys()):
            msgs = cc_by_number[cc_num]
            cc_name = cc_names.get(cc_num, f'CC{cc_num}')
            values = [msg.value for msg in msgs]
            print(f"      CC{cc_num:3} ({cc_name:15}): {len(msgs):3} messages, "
                  f"values {min(values):3}-{max(values):3}")
        
        print(f"\n   First 10 CC messages:")
        for i, msg in enumerate(cc_messages[:10]):
            cc_name = cc_names.get(msg.control, f'CC{msg.control}')
            print(f"      {i+1:2}. Ch{msg.channel:2} CC{msg.control:3} "
                  f"({cc_name:15}) = {msg.value:3} @ time {msg.time}")
    
    # Note info
    print(f"\n🎵 Note Messages: {len(note_messages)}")
    if note_messages:
        note_ons = [m for m in note_messages if m.type == 'note_on' and m.velocity > 0]
        if note_ons:
            notes = [m.note for m in note_ons]
            print(f"   Note range: {min(notes)} - {max(notes)}")
            print(f"   First note: {note_ons[0].note} (velocity {note_ons[0].velocity})")
    
    # Pitch bend info
    print(f"\n🎵 Pitch Bend Messages: {len(pitchwheel_messages)}")
    if pitchwheel_messages:
        pitches = [m.pitch for m in pitchwheel_messages]
        print(f"   Pitch range: {min(pitches)} - {max(pitches)}")
    
    print(f"\n{'='*60}\n")
    
    # Summary for web browser testing
    if len(cc_messages) > 0:
        print("✅ This file SHOULD show CC events in the HTML player.")
        print("   If the HTML player shows 0 CC events, it's a parser bug.")
    else:
        print("⚠️  This file has NO CC events - HTML player is correct.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_midi_cc.py <midi_file>")
        print("\nQuick test with existing file:")
        test_file = Path('midi_output/pala1_violin_swam.mid')
        if test_file.exists():
            analyze_midi_file(test_file)
        else:
            print(f"File not found: {test_file}")
    else:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        analyze_midi_file(filepath)
