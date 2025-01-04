import lxml.etree as LE


NOTES_IN_OCTAVE = 12
BASE_OCTAVE_OFFSET = 1

# TODO Look for dynamics in measure

"""
Items to store:
X position (Visual)
Y position (Visual)
Pitch
    Step (Letter)
    Octave
Rest?
Duration (Ticks)
Voice
Type (Visual)
Dot (Visual)
Stem (Visual)
Staff
Beam Visual
Tie: Type
Notation:
    Slur (Number to seperate?)
    Articulation
        Accent
        Tenuto
        Staccato
"""

class Pitch:
    def __init__ (self, step: str, octave: int):
        self.step = step
        self.octave = octave

class Notation:
    def __init__ (self):
        self.tied: str = ""
        self.slur: str = ""
        self.accent = False
        self.tenuto = False
        self.staccato = False

class XMLNote:
    def __init__(
        self,
        start_tick: int,
        tick_duration: int,
        staff: int,
        voice: int,
    ) -> None:
        """
        Object that represents a single note/chord from an musicxml file.

        param note_start: An integer that represents the start time of the note(s) in terms of musicXML ticks.
        param duration: An integer that represents the total duration the note(s) in terms of musicXML ticks.
        param midi_pitch: An integer that represents the pitch of the note equivilent to the midi pitch number.
        param velocity: An integer that represents the volume of the note(s) similar to midi velocity.
        param modifiers: TODO
        """
        self.start_tick = start_tick
        """The number of musicxml ticks as an integer from the piece start to beginning to play this note."""
        self.tick_duration = tick_duration
        """The number of musicxml ticks as an integer from the start of the note to the end of the note."""
        self.staff: int = staff
        """TODO"""
        self.voice: int = voice
        """TODO"""
        
        self.pitch: Pitch = Pitch("", 0) # This is just a default.

        self.rest: bool = False

        self.tie: str = ""

        self.notation: Notation = Notation()


        #VVV visual only. Not giving a focus

        self.x_position: float
        self.y_position: float
        self.note_type: str
        self.dot: bool = False
        self.stem: str 
        self.beam: str

        
    def set_pitch(self, pitch: Pitch):
        """TODO"""
        self.pitch = pitch


    def __str__(self) -> str:
        return f"Start: {self.start_tick}, Duration: {self.tick_duration}, Pitch: {self.pitch}"

    def __repr__(self) -> str:
        return f"Start: {self.start_tick}, Duration: {self.tick_duration}, Pitch: {self.pitch}"


class XMLBackup:
    def __init__(self, start_tick: int, tick_count: int) -> None:
        self.start_tick = start_tick
        self.tick_count = tick_count

class XMLMetronome:
    def __init__(self):
        self.parathesis = ""
        self.x_position: float = 0.0
        self.y_position: float = 0.0
        self.x_relative: float = 0.0
        self.y_relative: float = 0.0
        self.beat_unit = ""
        self.per_minute = 0

class XMLDynamics:
    def __init__(self):
        self.x_position: float = 0.0
        self.y_position: float = 0.0
        self.x_relative: float = 0.0
        self.y_relative: float = 0.0
        self.dynamic = ""

class XMLWedge:
    def __init__(self, wedge_type: str, number):

        self.wedge_type = wedge_type #ENUM?
        self.number = number

        self.x_position: float = 0.0
        self.y_position: float = 0.0
        self.x_relative: float = 0.0
        self.y_relative: float = 0.0

class XMLWords:
    def __init__(self, text: str):
        self.text = text

class XMLDashes:
    def __init__(self, dashes_type: str, number: int):
        self.dashes_type = dashes_type
        self.number = number

class XMLDirection:
    def __init__(self, start_tick: int):

        self.start_tick = start_tick


        self.direction_type = []

        self.tempo = 0

        self.dynamics = 0



        #VVV Visual
        self.placement = ""

class XMLBarline:
    def __init__(self, style: str, repeat_direction: str):
        self.style = style #ENUM?
        self.repeat_direction = repeat_direction #ENUM?

class XMLAttribute:
    def __init__(self, beat, beat_type):
        self.beat = beat
        self.beat_type = beat_type

class XMLMeasure:
    def __init__(self, start_tick: int) -> None:
        self.start_tick = start_tick
        self.note_list: list[XMLNote] = []
        self.backup_list: list[XMLBackup] = []

        self.position = 0

        self.barline_start = ""
        self.barline_stop = ""

        self.divitions = 0

        self.staves = 0

        self.clef = []

        self.print = ""

class PartInfo:
    def __init__(self, id: str, staff_count: int, divisions: int) -> None:
        """
        Object that stores all the information needed to identify the unique part.
        """
        self.id = id
        self.staff_count = staff_count
        self.divisions = divisions


class XMLStaffList:
    def __init__(self, part_info: PartInfo, staff_number: int) -> None:
        """
        A list of XMLNotes for a given part id and staff number.

        param part_id: The musicxml part id as a string.
        param staff_number: The musicxml staff number for a given part id as an integer.
        """
        self.notes: list[XMLNote] = []
        """List of XMLNotes for the part id for a specific staff number."""
        self.rests: list[XMLRest] = []
        """List of XMLRests for the part id for a specific staff number."""

        self.tempos: list[XMLTempo] = []

        self.dynamics: list[XMLDynamic] = []

        self.modifiers: list[XMLDynamic] = []

        self.part_info = part_info
        """Musicxml part id."""
        self.staff_number = staff_number
        """Musicxml staff number."""

    def append_note(self, note: XMLNote) -> None:
        """Append a XMLNote to notes."""
        self.notes.append(note)

    def append_rest(self, rest: XMLRest) -> None:
        """Append a XMLNote to notes."""
        self.rests.append(rest)

    def append_tempo(self, tempo: XMLTempo) -> None:
        self.tempos.append(tempo)

    def append_dynamic(self, dynamic: XMLDynamic) -> None:
        self.dynamics.append(dynamic)

    def append_modifier(self, modifier: XMLModifier) -> None:
        self.modifiers.append(modifier)

    def __str__(self) -> str:
        temp = ""
        for note in self.notes:
            temp += str(note) + "\n"
        return temp

    def __iter__(self):  # TODO Type hint?
        return iter(self.notes)


class MusicXML:
    def __init__(self, path: str) -> None:
        """
        Object that reads in a musicxml file and finds all the unique parts.

        param path: String path for the file that should be used.
        """
        self.file = LE.parse(path)
        """The parsed file."""
        self.root = self.file.getroot()
        """The root element from the parsed file."""
        self.part_info = self.find_part_info()
        """List of each unique part."""
        self.note_lists: list[XMLList] = []

        self.note_start: int = 0
        self.note_duration: int = 0
        self.previous_duration: int = 0