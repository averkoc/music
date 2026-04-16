"""Comprehensive catalog of all musical inference and automatic features in the code."""

print("=" * 80)
print("MUSICAL INFERENCE & AUTOMATIC FEATURES")
print("Beyond Explicit Score Markings")
print("=" * 80)

features = {
    "1. METRICAL EMPHASIS (NEW)": {
        "What": "Automatically emphasizes downbeats and strong beats",
        "Source": "beatStrength from MusicXML time signature",
        "Inference": "Downbeats (1.0) get +5 CC11, medium beats +2.5, weak beats +1.25",
        "Config": "swam_config.json → metrical_emphasis.enabled, emphasis_amount",
        "Default": "ENABLED (emphasis_amount: 5)"
    },
    
    "2. INTERVAL-AWARE PORTAMENTO (Phase 1)": {
        "What": "Adds pitch slides between notes based on interval size",
        "Source": "Calculated from consecutive pitches",
        "Inference": "Half-step: CC5=6, Whole-step: CC5=12, Third: CC5=21, Fourth+: CC5=30",
        "Config": "swam_config.json → portamento.enabled, base_amount, interval_scaling",
        "Default": "ENABLED (base_amount: 60)"
    },
    
    "3. ATTACK ENVELOPES (Phase 1)": {
        "What": "Natural attack curves on plain notes (no articulation)",
        "Source": "Generated for unmarked notes",
        "Inference": "Soft start (75% CC11) → ramp to full over 20 ticks",
        "Config": "Hardcoded in process_musicxml.py",
        "Default": "ALWAYS ACTIVE on plain notes"
    },
    
    "4. DYNAMIC ESTIMATION": {
        "What": "Guesses target dynamics for hairpins without end marking",
        "Source": "Start dynamic ± 2 levels",
        "Inference": "Crescendo: +2 levels (mf→ff), Diminuendo: -2 levels (f→mp)",
        "Config": "Hardcoded in articulation_detector.py _estimate_end_dynamic()",
        "Default": "ALWAYS ACTIVE for incomplete hairpins"
    },
    
    "5. PITCH-DEPENDENT VIBRATO": {
        "What": "Adjusts vibrato depth and rate based on register",
        "Source": "MIDI pitch number",
        "Inference": "Low notes: wider/slower, High notes: narrower/faster",
        "Config": "swam_config.json → articulations.vibrato_mark.pitch_dependent",
        "Default": "ENABLED (low: CC1=70/CC17=60, high: CC1=55/CC17=75)"
    },
    
    "6. BASELINE VIBRATO": {
        "What": "Subtle vibrato on all sustained notes (quarter+ duration)",
        "Source": "Note duration check",
        "Inference": "Adds CC1=20-28 automatically, excluded from staccato/short notes",
        "Config": "swam_config.json → articulations.default_vibrato.enabled",
        "Default": "CHECK CONFIG (likely enabled)"
    },
    
    "7. CC2 COUPLING (Breath/Bow Pressure)": {
        "What": "Automatically generates CC2 from CC11 values",
        "Source": "Mathematical formula from CC11",
        "Inference": "CC2 = f(CC11) to maintain physical modeling consistency",
        "Config": "Hardcoded in swam_cc_mapper.py _cc11_to_cc2()",
        "Default": "ALWAYS ACTIVE"
    },
    
    "8. NOTE-OFF VELOCITY": {
        "What": "Infers bow release speed from articulation type",
        "Source": "Articulation type",
        "Inference": "Staccato: 110 (sharp), Slur: 20 (smooth), Default: 64",
        "Config": "Hardcoded in process_musicxml.py",
        "Default": "ALWAYS ACTIVE"
    },
    
    "9. DURATION ADJUSTMENTS": {
        "What": "Modifies note lengths for articulations",
        "Source": "Articulation type",
        "Inference": "Staccato: 35%, Staccatissimo: 20%, Glissando: extends to overlap",
        "Config": "swam_config.json → articulations.staccato.note_duration_percent",
        "Default": "ALWAYS ACTIVE for articulated notes"
    },
    
    "10. HUMANIZATION (Optional)": {
        "What": "Random variations in timing, velocity, expression",
        "Source": "Random number generator",
        "Inference": "Timing jitter: ±10ms, Velocity: ±8, CC11 flutter: ±3",
        "Config": "Command line: --humanize, --humanize-subtle, --humanize-aggressive",
        "Default": "DISABLED (precise mode)"
    },
    
    "11. VIBRATO JITTER": {
        "What": "Natural variation during note sustain",
        "Source": "Random fluctuation of CC1 during note",
        "Inference": "Subtle CC1 wobble for realistic vibrato",
        "Config": "swam_config.json → articulations.vibrato_mark.jitter",
        "Default": "CURRENTLY DISABLED (timing issues) - see code comment"
    },
    
    "12. ARTICULATION CC PATTERNS": {
        "What": "Complex CC envelopes for each articulation type",
        "Source": "Articulation marks",
        "Inference": "Accent: spike to 110, Marcato: spike to 120, with decay curves",
        "Config": "swam_config.json → articulations.{staccato,accent,etc}",
        "Default": "ALWAYS ACTIVE when articulation detected"
    },
    
    "13. BOW FORCE/POSITION": {
        "What": "CC20/CC21 adjustments for articulations",
        "Source": "Articulation type",
        "Inference": "Staccato: higher force, Sul ponticello: adjusted position",
        "Config": "Hardcoded for violin, varies by articulation",
        "Default": "ACTIVE for violin only"
    }
}

print("\n" + "=" * 80)
print("SUMMARY OF AUTOMATIC FEATURES:")
print("=" * 80)

for i, (name, details) in enumerate(features.items(), 1):
    print(f"\n{name}")
    print("-" * 80)
    for key, value in details.items():
        print(f"  {key:12}: {value}")

print("\n" + "=" * 80)
print("CATEGORIZATION:")
print("=" * 80)

print("\nALWAYS ACTIVE (cannot disable):")
print("  - Attack envelopes (#3)")
print("  - CC2 coupling (#7)")
print("  - Note-off velocity (#8)")
print("  - Duration adjustments (#9)")
print("  - Articulation CC patterns (#12)")
print("  - Bow force/position (#13)")

print("\nCONFIGURABLE (can enable/disable in swam_config.json):")
print("  - Metrical emphasis (#1)")
print("  - Interval-aware portamento (#2)")
print("  - Pitch-dependent vibrato (#5)")
print("  - Baseline vibrato (#6)")

print("\nOPTIONAL (command-line flags):")
print("  - Humanization (#10)")

print("\nESTIMATED (when score info incomplete):")
print("  - Dynamic estimation (#4)")

print("\nDISABLED (implementation issues):")
print("  - Vibrato jitter (#11)")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print("\nFor MAXIMUM control (minimal inference):")
print("  1. Disable metrical_emphasis in config")
print("  2. Disable portamento in config")
print("  3. Disable default_vibrato in config")
print("  4. Add ALL dynamics explicitly to score (no hairpins without end marking)")
print("  5. Use --precise mode (no humanization)")
print("\nFor REALISTIC performance (moderate inference):")
print("  Keep defaults, but add explicit end dynamics to all hairpins")
print("=" * 80)
