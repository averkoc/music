"""Analyze structural context usage in the architecture."""

print("=" * 80)
print("STRUCTURAL CONTEXT IN ARTICULATION → SWAM MAPPING")
print("=" * 80)

architecture = {
    "LEVEL 1: Note Properties (Local Context)": {
        "Tracked": [
            "pitch (MIDI number)",
            "duration (quarter notes)",
            "onset_time (from start)",
            "velocity",
            "articulations (list)",
            "dynamic_level",
            "expression_text"
        ],
        "Usage": "Direct mapping to CC values (pitch → vibrato depth, dynamic → CC11)",
        "Structural_Awareness": "NONE - note in isolation"
    },
    
    "LEVEL 2: Phrase Context (Membership)": {
        "Tracked": [
            "✓ in_slur: bool - Is this note inside a slur?",
            "✓ beat_strength: float - Metrical position (downbeat=1.0)",
            "✓ note_index: int - Sequential position in piece",
            "✓ total_notes: int - Total notes in piece"
        ],
        "Usage": {
            "in_slur": "→ Changes note-off velocity (20 vs 64), enables legato CC64",
            "beat_strength": "→ Adds metrical emphasis to CC11 (downbeats +5)",
            "note_index + total_notes": "→ Currently PASSED but UNUSED in CC generation"
        },
        "Structural_Awareness": "PARTIAL - knows membership but limited use"
    },
    
    "LEVEL 3: Sequential Context (Previous/Next Notes)": {
        "Tracked": [
            "✓ prev_pitch (stored between notes)",
            "✓ last_cc11_value, last_cc1_value, last_cc20_value, last_cc21_value"
        ],
        "Usage": {
            "prev_pitch": "→ Calculates interval → portamento amount (CC5)",
            "last_cc*": "→ Smooth transitions (avoided abrupt CC jumps)"
        },
        "Structural_Awareness": "YES - interval-aware, state-aware"
    },
    
    "LEVEL 4: Hierarchical Context (NOT TRACKED)": {
        "Missing": [
            "✗ measure_number (detected but not stored in NoteArticulation)",
            "✗ phrase_id (which phrase/section is this note in?)",
            "✗ slur_id (which slur does this belong to?)",
            "✗ position_in_slur (first note? last note? middle?)",
            "✗ position_in_measure (first beat tracked via beatStrength, but not explicitly)",
            "✗ dynamic_wedge_context (is note inside crescendo/diminuendo?)",
            "✗ tempo_context (tempo at this point)"
        ],
        "Potential_Usage": "Could affect bow position drift, vibrato onset delay, phrase shaping",
        "Current_State": "NOT IMPLEMENTED"
    }
}

print("\n" + "=" * 80)
for level, details in architecture.items():
    print(f"\n{level}")
    print("-" * 80)
    
    if "Tracked" in details:
        print("\nCurrent tracking:")
        for item in details["Tracked"]:
            symbol = "✓" if item.startswith("✓") else "✗" if item.startswith("✗") else " "
            print(f"  {item}")
    
    if "Missing" in details:
        print("\nMissing:")
        for item in details["Missing"]:
            print(f"  {item}")
    
    if isinstance(details.get("Usage"), dict):
        print("\nHow structural context affects SWAM mapping:")
        for key, value in details["Usage"].items():
            print(f"  • {key}")
            print(f"    {value}")
    elif "Usage" in details:
        print(f"\nUsage: {details['Usage']}")
    
    if "Structural_Awareness" in details:
        print(f"\nStructural awareness: {details['Structural_Awareness']}")

print("\n" + "=" * 80)
print("CONCRETE EXAMPLES OF STRUCTURAL CONTEXT AFFECTING CC MAPPING:")
print("=" * 80)

examples = {
    "1. Slur Membership Changes Articulation": {
        "Context": "Note is inside a slur (in_slur=True)",
        "Effect": [
            "Note-off velocity: 20 (smooth) instead of 64 (normal)",
            "This makes legato bow connection instead of separate bow stroke",
            "SWAM physical model responds differently to low note-off velocity"
        ],
        "Code": "process_musicxml.py line 291: elif note_art.in_slur: note_off_velocity = 20"
    },
    
    "2. Beat Position Changes Expression": {
        "Context": "Note on downbeat (beat_strength=1.0)",
        "Effect": [
            "CC11 gets +5 boost (metrical emphasis)",
            "Note on weak beat (0.25) only gets +1.25",
            "Creates natural metrical shaping without explicit accents"
        ],
        "Code": "process_musicxml.py: beat_emphasis = int(note_art.beat_strength * emphasis_amount)"
    },
    
    "3. Interval Context Changes Portamento": {
        "Context": "Large leap (e.g., octave jump from previous note)",
        "Effect": [
            "CC5 portamento = 30 for large interval",
            "CC5 portamento = 6 for half-step",
            "Same articulation (no gliss mark) but different slide amount"
        ],
        "Code": "Phase 1 portamento uses prev_pitch to calculate interval"
    },
    
    "4. Pitch Register Changes Vibrato": {
        "Context": "Note is in high register (>D5)",
        "Effect": [
            "CC1 depth = 55 (narrower) vs 70 for low notes",
            "CC17 rate = 75 (faster) vs 60 for low notes",
            "String-appropriate vibrato characteristics"
        ],
        "Code": "process_musicxml.py: pitch_dependent vibrato config"
    }
}

for name, details in examples.items():
    print(f"\n{name}")
    print("-" * 80)
    print(f"Context: {details['Context']}")
    print(f"\nEffect on SWAM CC mapping:")
    for effect in details["Effect"]:
        print(f"  • {effect}")
    print(f"\nCode location: {details['Code']}")

print("\n" + "=" * 80)
print("UNUSED STRUCTURAL INFORMATION:")
print("=" * 80)

unused = {
    "note_index / total_notes": {
        "What": "Position in piece (note 23 of 150)",
        "Currently": "Passed to _generate_cc_for_note but never used",
        "Could Enable": [
            "Gradual bow wear (position drift over piece)",
            "Fatigue modeling (vibrato depth decreases)",
            "Phrase arc shaping (opening vs closing phrases)"
        ]
    },
    
    "measure_number": {
        "What": "Which measure the note is in",
        "Currently": "Detected in articulation_detector but not stored",
        "Could Enable": [
            "Phrase boundary detection",
            "Breathing points (wind instruments)",
            "Bow direction planning (violin)"
        ]
    },
    
    "Dynamic wedge membership": {
        "What": "Is note inside a crescendo/diminuendo?",
        "Currently": "Wedges applied separately, notes don't know context",
        "Could Enable": [
            "Coordinate CC11 with wedge trajectory",
            "Adjust vibrato intensity during crescendo"
        ]
    }
}

for name, details in unused.items():
    print(f"\n{name}:")
    print(f"  What: {details['What']}")
    print(f"  Currently: {details['Currently']}")
    print(f"  Could enable:")
    for item in details["Could Enable"]:
        print(f"    - {item}")

print("\n" + "=" * 80)
print("SUMMARY: YOUR ARCHITECTURE STATUS")
print("=" * 80)
print("""
YES, you have structural membership affecting articulation mapping:

✓ PHRASE MEMBERSHIP (partial):
  - Slur context changes note-off velocity & legato
  - Beat position adds metrical emphasis
  - Interval context affects portamento

✓ SEQUENTIAL CONTEXT (good):
  - Previous pitch influences current portamento
  - Previous CC values ensure smooth transitions
  - Pitch register affects vibrato characteristics

✗ HIERARCHICAL CONTEXT (missing):
  - No measure boundaries used for phrase shaping
  - No position-in-phrase awareness
  - Note index tracked but unused
  
✗ MULTI-NOTE COORDINATION (missing):
  - Dynamic wedges applied separately from notes
  - No bow direction planning across phrase
  - No breath phrase awareness

ARCHITECTURE PATTERN:
  Note properties + Local context → CC values
  (Strong at note-by-note, weak at phrase-level coordination)
""")
print("=" * 80)
