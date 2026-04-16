#!/usr/bin/env python3
"""
MIDI Output Recorder and Comparator

Records live MIDI output from loopMIDI (or other virtual MIDI port) with precise
timestamps, then allows comparison of two recordings to verify timing accuracy.

Usage:
    1. Record Ableton Live output:
       python record_midi_output.py --record ableton_recording.json
       
    2. Record webpage output:
       python record_midi_output.py --record webpage_recording.json
       
    3. Compare the two:
       python record_midi_output.py --compare ableton_recording.json webpage_recording.json

Requirements:
    pip install mido python-rtmidi
"""

import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

try:
    import mido
    from mido import open_input
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install mido python-rtmidi")
    exit(1)


class MIDIRecorder:
    """Records MIDI messages with high-precision timestamps"""
    
    def __init__(self, port_name: str = None):
        self.messages: List[Dict[str, Any]] = []
        self.start_time: float = 0
        self.port_name = port_name
        
    def list_ports(self) -> List[str]:
        """List available MIDI input ports"""
        return mido.get_input_names()
    
    def record(self, duration_seconds: int = None, port_name: str = None):
        """
        Record MIDI messages from specified port
        
        Args:
            duration_seconds: How long to record (None = until Ctrl+C)
            port_name: MIDI port to listen to (None = auto-detect loopMIDI)
        """
        # Find port
        available_ports = self.list_ports()
        
        if not available_ports:
            print("❌ No MIDI input ports found!")
            print("   Make sure loopMIDI or IAC Driver is running")
            return False
        
        print("\n📋 Available MIDI Input Ports:")
        for i, port in enumerate(available_ports):
            print(f"   {i+1}. {port}")
        print()
        
        if port_name:
            target_port = port_name
        else:
            # Auto-detect loopMIDI or virtual port
            for port in available_ports:
                name_lower = port.lower()
                if 'loopmidi' in name_lower or 'iac' in name_lower or 'virtual' in name_lower:
                    target_port = port
                    break
            else:
                target_port = available_ports[0]
        
        print(f"🎹 Recording from: {target_port}")
        
        if duration_seconds:
            print(f"⏱️  Duration: {duration_seconds} seconds")
        else:
            print("⏱️  Duration: Until Ctrl+C")
        
        print("\n✅ Recording started...")
        print("   Play your MIDI file now!\n")
        
        try:
            with mido.open_input(target_port) as inport:
                self.start_time = time.time()
                start_monotonic = time.perf_counter()
                
                message_count = 0
                last_print = 0
                
                for msg in inport:
                    # Use perf_counter for high precision
                    timestamp = time.perf_counter() - start_monotonic
                    
                    # Store message with timestamp
                    msg_data = {
                        'timestamp': timestamp,
                        'type': msg.type,
                        'bytes': list(msg.bytes()) if hasattr(msg, 'bytes') else None
                    }
                    
                    # Add message-specific fields
                    if hasattr(msg, 'note'):
                        msg_data['note'] = msg.note
                    if hasattr(msg, 'velocity'):
                        msg_data['velocity'] = msg.velocity
                    if hasattr(msg, 'control'):
                        msg_data['control'] = msg.control
                    if hasattr(msg, 'value'):
                        msg_data['value'] = msg.value
                    if hasattr(msg, 'channel'):
                        msg_data['channel'] = msg.channel
                    
                    self.messages.append(msg_data)
                    message_count += 1
                    
                    # Print progress every second
                    if timestamp - last_print >= 1.0:
                        print(f"   📊 {message_count} messages recorded ({timestamp:.1f}s)")
                        last_print = timestamp
                    
                    # Check duration
                    if duration_seconds and timestamp >= duration_seconds:
                        break
                        
        except KeyboardInterrupt:
            print("\n⏹️  Recording stopped by user")
        except Exception as e:
            print(f"\n❌ Error during recording: {e}")
            return False
        
        total_time = time.perf_counter() - start_monotonic
        print(f"\n✅ Recording complete!")
        print(f"   Total messages: {message_count}")
        print(f"   Duration: {total_time:.2f}s")
        
        return True
    
    def save(self, filepath: Path):
        """Save recording to JSON file"""
        data = {
            'start_time': self.start_time,
            'messages': self.messages,
            'message_count': len(self.messages),
            'duration': self.messages[-1]['timestamp'] if self.messages else 0
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Saved recording to: {filepath}")
    
    @staticmethod
    def load(filepath: Path) -> 'MIDIRecorder':
        """Load recording from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        recorder = MIDIRecorder()
        recorder.start_time = data['start_time']
        recorder.messages = data['messages']
        
        return recorder


def compare_recordings(rec1_path: Path, rec2_path: Path):
    """
    Compare two MIDI recordings for timing accuracy
    
    Args:
        rec1_path: Path to first recording (reference)
        rec2_path: Path to second recording (to compare)
    """
    print("\n" + "="*80)
    print("MIDI OUTPUT COMPARISON")
    print("="*80)
    
    # Load recordings
    rec1 = MIDIRecorder.load(rec1_path)
    rec2 = MIDIRecorder.load(rec2_path)
    
    print(f"\n📁 Recording 1: {rec1_path.name}")
    print(f"   Messages: {len(rec1.messages)}")
    print(f"   Duration: {rec1.messages[-1]['timestamp']:.2f}s")
    
    print(f"\n📁 Recording 2: {rec2_path.name}")
    print(f"   Messages: {len(rec2.messages)}")
    print(f"   Duration: {rec2.messages[-1]['timestamp']:.2f}s")
    
    # Compare message counts
    if len(rec1.messages) != len(rec2.messages):
        print(f"\n⚠️  WARNING: Different number of messages!")
        print(f"   Recording 1: {len(rec1.messages)} messages")
        print(f"   Recording 2: {len(rec2.messages)} messages")
    
    # Extract note events for timing comparison
    notes1 = [(msg['timestamp'], msg.get('note'), msg.get('velocity')) 
              for msg in rec1.messages if msg['type'] == 'note_on']
    notes2 = [(msg['timestamp'], msg.get('note'), msg.get('velocity')) 
              for msg in rec2.messages if msg['type'] == 'note_on']
    
    print("\n" + "="*80)
    print("NOTE TIMING COMPARISON (First 20 notes)")
    print("="*80)
    print(f"{'Note':<8} {'Rec1 Time':<12} {'Rec2 Time':<12} {'Difference':<15} {'Status'}")
    print("-"*80)
    
    timing_diffs = []
    max_timing_error = 0
    
    for i in range(min(20, len(notes1), len(notes2))):
        time1, note1, vel1 = notes1[i]
        time2, note2, vel2 = notes2[i]
        
        diff_ms = (time2 - time1) * 1000  # Convert to milliseconds
        timing_diffs.append(diff_ms)
        max_timing_error = max(max_timing_error, abs(diff_ms))
        
        pitch_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note1 % 12]
        octave = note1 // 12 - 1
        
        if note1 != note2:
            status = "⚠️  WRONG NOTE"
        elif abs(diff_ms) > 50:  # > 50ms is noticeable
            status = "⚠️  TIMING OFF"
        elif abs(diff_ms) > 10:  # > 10ms is measurable
            status = "~OK (slight)"
        else:
            status = "✓ PERFECT"
        
        print(f"{pitch_name}{octave:<6} {time1:<12.3f} {time2:<12.3f} {diff_ms:+.1f} ms       {status}")
    
    # Statistics
    print("\n" + "="*80)
    print("TIMING STATISTICS")
    print("="*80)
    
    if timing_diffs:
        avg_diff = sum(timing_diffs) / len(timing_diffs)
        abs_diffs = [abs(d) for d in timing_diffs]
        avg_abs_diff = sum(abs_diffs) / len(abs_diffs)
        
        print(f"\nAverage timing difference: {avg_diff:+.2f} ms")
        print(f"Average absolute difference: {avg_abs_diff:.2f} ms")
        print(f"Maximum timing error: {max_timing_error:.2f} ms")
        
        if max_timing_error < 10:
            print("\n✅ EXCELLENT: Timing accuracy within 10ms!")
        elif max_timing_error < 50:
            print("\n✓ GOOD: Timing accuracy acceptable (< 50ms)")
        else:
            print("\n⚠️  WARNING: Timing errors exceed 50ms threshold")
    
    # Compare CC messages
    cc_types1 = defaultdict(int)
    cc_types2 = defaultdict(int)
    
    for msg in rec1.messages:
        if msg['type'] == 'control_change':
            cc_types1[msg.get('control')] += 1
    
    for msg in rec2.messages:
        if msg['type'] == 'control_change':
            cc_types2[msg.get('control')] += 1
    
    print("\n" + "="*80)
    print("CC MESSAGE COMPARISON")
    print("="*80)
    
    all_ccs = sorted(set(list(cc_types1.keys()) + list(cc_types2.keys())))
    
    cc_names = {
        1: "Modulation/Vibrato",
        2: "Breath",
        5: "Portamento",
        11: "Expression",
        17: "Vibrato Rate",
        20: "Harmonics",
        21: "Brightness Offset",
        64: "Sustain",
        74: "Brightness",
        120: "All Sound Off",
        123: "All Notes Off"
    }
    
    print(f"\n{'CC#':<5} {'Name':<20} {'Rec1 Count':<12} {'Rec2 Count':<12} {'Difference'}")
    print("-"*80)
    
    for cc in all_ccs:
        count1 = cc_types1[cc]
        count2 = cc_types2[cc]
        diff = count2 - count1
        name = cc_names.get(cc, f"CC{cc}")
        
        status = ""
        if diff != 0:
            status = f" ({diff:+d})"
        
        print(f"{cc:<5} {name:<20} {count1:<12} {count2:<12} {diff:+d}{status}")
    
    # Overall assessment
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)
    
    identical_msgs = len(rec1.messages) == len(rec2.messages)
    identical_ccs = cc_types1 == cc_types2
    timing_good = max_timing_error < 50 if timing_diffs else False
    
    if identical_msgs and identical_ccs and timing_good:
        print("\n✅ OUTPUTS ARE EQUIVALENT!")
        print("   Same message count, same CC distribution, excellent timing")
    else:
        issues = []
        if not identical_msgs:
            issues.append("different message counts")
        if not identical_ccs:
            issues.append("different CC distribution")
        if not timing_good:
            issues.append("timing errors > 50ms")
        
        print(f"\n⚠️  DIFFERENCES DETECTED: {', '.join(issues)}")


def main():
    parser = argparse.ArgumentParser(
        description="Record and compare MIDI output for timing verification"
    )
    parser.add_argument('--record', metavar='OUTPUT_FILE',
                       help='Record MIDI output to JSON file')
    parser.add_argument('--compare', nargs=2, metavar=('FILE1', 'FILE2'),
                       help='Compare two recordings')
    parser.add_argument('--port', help='MIDI port name to record from')
    parser.add_argument('--duration', type=int, 
                       help='Recording duration in seconds (default: until Ctrl+C)')
    parser.add_argument('--list-ports', action='store_true',
                       help='List available MIDI ports')
    
    args = parser.parse_args()
    
    if args.list_ports:
        print("\n📋 Available MIDI Input Ports:")
        ports = mido.get_input_names()
        for i, port in enumerate(ports):
            print(f"   {i+1}. {port}")
        return
    
    if args.record:
        recorder = MIDIRecorder()
        if recorder.record(duration_seconds=args.duration, port_name=args.port):
            recorder.save(Path(args.record))
    
    elif args.compare:
        file1 = Path(args.compare[0])
        file2 = Path(args.compare[1])
        
        if not file1.exists():
            print(f"❌ File not found: {file1}")
            return
        if not file2.exists():
            print(f"❌ File not found: {file2}")
            return
        
        compare_recordings(file1, file2)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
