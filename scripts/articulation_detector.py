"""
MusicXML Articulation Detector

Extracts articulation, dynamic, and expression data from MusicXML files
for accurate SWAM CC mapping.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ArticulationType(Enum):
    """Types of articulations found in MusicXML."""
    STACCATO = "staccato"
    STACCATISSIMO = "staccatissimo"
    TENUTO = "tenuto"
    ACCENT = "accent"
    STRONG_ACCENT = "strong-accent"
    MARCATO = "marcato"
    LEGATO = "legato"
    SLUR = "slur"
    SPICCATO = "spiccato"
    DETACHE = "detache"
    CRESCENDO = "crescendo"
    DIMINUENDO = "diminuendo"
    VIBRATO = "vibrato"
    TREMOLO = "tremolo"
    SUL_PONTICELLO = "sul-ponticello"
    SUL_TASTO = "sul-tasto"
    PORTAMENTO = "portamento"
    GLISSANDO = "glissando"


class DynamicLevel(Enum):
    """Dynamic markings in order of intensity."""
    PPPP = ("pppp", 10)
    PPP = ("ppp", 20)
    PP = ("pp", 35)
    P = ("p", 50)
    MP = ("mp", 65)
    MF = ("mf", 80)
    F = ("f", 95)
    FF = ("ff", 110)
    FFF = ("fff", 120)
    FFFF = ("ffff", 127)
    
    def __init__(self, marking: str, cc_value: int):
        self.marking = marking
        self.cc_value = cc_value


@dataclass
class NoteArticulation:
    """Articulation data for a single note."""
    note_index: int
    pitch: int
    duration: float  # in quarter notes
    onset_time: float  # in quarter notes from start
    velocity: int
    articulations: List[ArticulationType]
    dynamic_level: Optional[DynamicLevel]
    in_slur: bool
    expression_text: Optional[str]
    beat_strength: float = 0.0  # Metrical weight: 1.0 = downbeat, 0.5 = medium, 0.25 = weak


@dataclass
class DynamicChange:
    """Dynamic change event (crescendo, diminuendo)."""
    start_time: float
    end_time: float
    start_dynamic: DynamicLevel
    end_dynamic: DynamicLevel
    is_crescendo: bool


class MusicXMLArticulationDetector:
    """
    Detects and extracts articulations from music21 Score objects.
    """
    
    def __init__(self):
        """Initialize the articulation detector."""
        self.current_dynamic: DynamicLevel = DynamicLevel.MF
        self.note_articulations: List[NoteArticulation] = []
        self.dynamic_changes: List[DynamicChange] = []
    
    def analyze_score(self, score) -> Tuple[List[NoteArticulation], List[DynamicChange]]:
        """
        Analyze a music21 Score and extract all articulation data.
        
        Args:
            score: music21.stream.Score object
            
        Returns:
            Tuple of (note articulations, dynamic changes)
        """
        from music21 import note, expressions, dynamics
        
        self.note_articulations = []
        self.dynamic_changes = []
        
        # Get the first part (melody line)
        if len(score.parts) == 0:
            return ([], [])
        
        part = score.parts[0]
        note_index = 0
        current_offset = 0.0
        
        # Track slur state (no longer manual tracking - using spanners below)
        slur_start_dynamic = self.current_dynamic
        
        # Collect glissando spanners
        glissando_starts = {}  # Maps note object to glissando spanner
        for gliss in part.flatten().getElementsByClass('Glissando'):
            if gliss.getFirst():
                glissando_starts[id(gliss.getFirst())] = gliss
        
        # Collect vibrato/trill spanners (wavy lines)
        vibrato_ranges = []  # List of (start_offset, end_offset) tuples
        for spanner in part.flatten().spanners:
            spanner_name = spanner.__class__.__name__.lower()
            # Check for wavy line, trill, or vibrato spanners
            if any(keyword in spanner_name for keyword in ['wavyline', 'trill', 'tremolo']):
                if spanner.getFirst() and spanner.getLast():
                    # Get absolute offsets (from start of piece, not measure)
                    first_note = spanner.getFirst()
                    last_note = spanner.getLast()
                    start_offset = first_note.getOffsetInHierarchy(part)
                    end_offset = last_note.getOffsetInHierarchy(part) + last_note.duration.quarterLength
                    vibrato_ranges.append((start_offset, end_offset))
        
        # Collect slur spanners        
        slur_ranges = []  # List of (start_offset, end_offset) tuples
        for spanner in part.flatten().spanners:
            if spanner.__class__.__name__ == 'Slur':
                if spanner.getFirst() and spanner.getLast():
                    # Get absolute offsets (from start of piece, not measure)
                    first_note = spanner.getFirst()
                    last_note = spanner.getLast()
                    start_offset = first_note.getOffsetInHierarchy(part)
                    end_offset = last_note.getOffsetInHierarchy(part) + last_note.duration.quarterLength
                    slur_ranges.append((start_offset, end_offset))
        
        # Iterate through all notes and dynamics
        for element in part.flatten().notesAndRests:
            if isinstance(element, note.Note):
                # Extract articulations
                articulations = self._extract_articulations(element)
                
                # Check for glissando starting on this note
                if id(element) in glissando_starts:
                    articulations.append(ArticulationType.GLISSANDO)
                
                # Check if note is within vibrato spanner range
                for start, end in vibrato_ranges:
                    if start <= element.offset < end:
                        articulations.append(ArticulationType.VIBRATO)
                        break
                
                # Check if note is within slur range
                in_slur = False
                for start, end in slur_ranges:
                    if start <= element.offset < end:
                        in_slur = True
                        break
                
                # Check for dynamic markings on this note
                dynamic = self._get_dynamic_at_element(element, part)
                if dynamic:
                    self.current_dynamic = dynamic
                
                # Get expression text
                expression_text = self._extract_expression_text(element)
                
                # Check for vibrato in expression text
                if expression_text and any(keyword in expression_text.lower() for keyword in ['vibrato', 'vib.', 'vib']):
                    articulations.append(ArticulationType.VIBRATO)
                
                # Get beat strength (0.0-1.0, where 1.0 = downbeat)
                beat_strength = element.beatStrength if hasattr(element, 'beatStrength') else 0.0
                
                # Create note articulation
                note_art = NoteArticulation(
                    note_index=note_index,
                    pitch=element.pitch.midi,
                    duration=element.quarterLength,
                    onset_time=element.offset,
                    velocity=self._dynamic_to_velocity(self.current_dynamic),
                    articulations=articulations,
                    dynamic_level=self.current_dynamic,
                    in_slur=in_slur,
                    expression_text=expression_text,
                    beat_strength=beat_strength
                )
                
                self.note_articulations.append(note_art)
                note_index += 1
        
        # Extract crescendo/diminuendo wedges
        self._extract_dynamic_wedges(part)
        
        return (self.note_articulations, self.dynamic_changes)
    
    def _extract_articulations(self, note_obj) -> List[ArticulationType]:
        """Extract articulations from a music21 Note object."""
        articulations = []
        
        # Check for tremolo ornaments first
        if hasattr(note_obj, 'expressions'):
            for expr in note_obj.expressions:
                expr_name = expr.__class__.__name__.lower()
                if 'tremolo' in expr_name:
                    articulations.append(ArticulationType.TREMOLO)
        
        for articulation in note_obj.articulations:
            art_name = articulation.__class__.__name__.lower()
            
            # MuseScore vibrato: Generic "Articulation" class (not a subclass)
            # These are often SMuFL wiggle/vibrato symbols that music21 doesn't parse specifically
            if art_name == 'articulation':
                # Likely a custom articulation like vibrato (wiggleVibratoLargeSlowest, etc.)
                articulations.append(ArticulationType.VIBRATO)
                continue
            
            # Check for MuseScore SMuFL vibrato symbols in string representation
            art_str = str(articulation).lower()
            if 'vibrato' in art_str or 'wiggle' in art_str:
                articulations.append(ArticulationType.VIBRATO)
                continue
            
            if 'staccatissimo' in art_name:
                articulations.append(ArticulationType.STACCATISSIMO)
            elif 'staccato' in art_name:
                articulations.append(ArticulationType.STACCATO)
            elif 'tenuto' in art_name:
                articulations.append(ArticulationType.TENUTO)
            elif 'strongaccent' in art_name or 'marcato' in art_name:
                articulations.append(ArticulationType.STRONG_ACCENT)
            elif 'accent' in art_name:
                articulations.append(ArticulationType.ACCENT)
            elif 'spiccato' in art_name:
                articulations.append(ArticulationType.SPICCATO)
            elif 'detache' in art_name:
                articulations.append(ArticulationType.DETACHE)
            elif 'tremolo' in art_name:
                articulations.append(ArticulationType.TREMOLO)
            elif 'vibrato' in art_name:
                articulations.append(ArticulationType.VIBRATO)
        
        return articulations
    
    def _get_dynamic_at_element(self, element, part) -> Optional[DynamicLevel]:
        """Get the dynamic marking at a specific element."""
        from music21 import dynamics
        
        # Check for dynamics at this offset
        dynamics_at_offset = part.flatten().getElementsByOffset(
            element.offset,
            element.offset + 0.1,
            includeEndBoundary=False,
            classList=[dynamics.Dynamic]
        )
        
        if len(dynamics_at_offset) > 0:
            dyn = dynamics_at_offset[0]
            dyn_value = dyn.value.lower() if hasattr(dyn, 'value') else str(dyn).lower()
            
            # Map to DynamicLevel
            for level in DynamicLevel:
                if level.marking == dyn_value:
                    return level
        
        return None
    
    def _extract_expression_text(self, note_obj) -> Optional[str]:
        """Extract expression text (like 'dolce', 'espressivo') from a note."""
        expression_texts = []
        
        for exp in note_obj.expressions:
            if hasattr(exp, 'content'):
                expression_texts.append(exp.content)
            elif hasattr(exp, 'name'):
                expression_texts.append(exp.name)
        
        return ', '.join(expression_texts) if expression_texts else None
    
    def _extract_dynamic_wedges(self, part):
        """Extract crescendo and diminuendo wedges."""
        from music21 import dynamics
        
        # Find all crescendo/diminuendo spanners
        for spanner in part.flatten().getElementsByClass('Crescendo'):
            start_time = spanner.getFirst().offset if spanner.getFirst() else 0.0
            end_time = spanner.getLast().offset if spanner.getLast() else start_time + 4.0
            
            # Estimate start and end dynamics
            start_dyn = self._get_dynamic_before(part, start_time)
            end_dyn = self._estimate_end_dynamic(start_dyn, is_crescendo=True)
            
            change = DynamicChange(
                start_time=start_time,
                end_time=end_time,
                start_dynamic=start_dyn,
                end_dynamic=end_dyn,
                is_crescendo=True
            )
            self.dynamic_changes.append(change)
        
        for spanner in part.flatten().getElementsByClass('Diminuendo'):
            start_time = spanner.getFirst().offset if spanner.getFirst() else 0.0
            end_time = spanner.getLast().offset if spanner.getLast() else start_time + 4.0
            
            start_dyn = self._get_dynamic_before(part, start_time)
            end_dyn = self._estimate_end_dynamic(start_dyn, is_crescendo=False)
            
            change = DynamicChange(
                start_time=start_time,
                end_time=end_time,
                start_dynamic=start_dyn,
                end_dynamic=end_dyn,
                is_crescendo=False
            )
            self.dynamic_changes.append(change)
    
    def _get_dynamic_before(self, part, offset: float) -> DynamicLevel:
        """Get the most recent dynamic marking before a given offset."""
        from music21 import dynamics
        
        dynamics_before = part.flatten().getElementsByClass(dynamics.Dynamic)
        
        last_dynamic = DynamicLevel.MF
        for dyn in dynamics_before:
            if dyn.offset < offset:
                dyn_value = dyn.value.lower() if hasattr(dyn, 'value') else str(dyn).lower()
                for level in DynamicLevel:
                    if level.marking == dyn_value:
                        last_dynamic = level
                        break
        
        return last_dynamic
    
    def _estimate_end_dynamic(self, start: DynamicLevel, is_crescendo: bool) -> DynamicLevel:
        """Estimate the end dynamic of a crescendo/diminuendo."""
        levels = list(DynamicLevel)
        current_index = levels.index(start)
        
        if is_crescendo:
            # Increase by 2-3 levels
            target_index = min(len(levels) - 1, current_index + 2)
        else:
            # Decrease by 2-3 levels
            target_index = max(0, current_index - 2)
        
        return levels[target_index]
    
    def _dynamic_to_velocity(self, dynamic: DynamicLevel) -> int:
        """Convert dynamic level to MIDI velocity."""
        return dynamic.cc_value
