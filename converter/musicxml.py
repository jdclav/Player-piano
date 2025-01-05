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


class XMLTickCounter:
    def __init__(self, start_tick: int = 0):
        self.tick = start_tick

    def set_tick(self, tick) -> None:
        self.tick = tick

    def get_tick(self) -> int:
        result = self.tick
        return result


class XMLPosition:
    def __init__(
        self,
        x_position: float,
        y_position: float,
        x_relative: float = 0.0,
        y_relative: float = 0.0,
    ):
        """
        TODO
        """

        self.x_position = x_position
        self.y_position = y_position
        self.x_relative = x_relative
        self.y_relative = y_relative


class XMLPitch:
    def __init__(self):
        self.step: str = "A"
        self.alter: float = 0
        self.octave: int = 0

    def set_pitch(self, pitch: LE._Element) -> None:
        self.step = pitch.find(".//step").text

        element_list = pitch.xpath(".//alter")
        if element_list:
            self.alter = float(element_list[0].text)

        self.octave = int(pitch.find(".//octave").text)


class XMLNotation:
    def __init__(self):
        self.tied: str = ""
        self.slur: str = ""
        self.accent = False
        self.tenuto = False
        self.staccato = False


class XMLNote:
    def __init__(self, note: LE._Element, tick: XMLTickCounter) -> None:
        """
        Object that represents a single note/chord from an musicxml file.

        param note_start: An integer that represents the start time of the note(s) in terms of musicXML ticks.
        param duration: An integer that represents the total duration the note(s) in terms of musicXML ticks.
        param midi_pitch: An integer that represents the pitch of the note equivilent to the midi pitch number.
        param velocity: An integer that represents the volume of the note(s) similar to midi velocity.
        param modifiers: TODO
        """
        self.start_tick = tick.get_tick()
        """The number of musicxml ticks as an integer from the piece start to beginning to play this note."""

        # self.grace = ""
        # self.cue = ""
        self.chord = False
        self.pitch = XMLPitch()
        # self.unpitched = ""
        self.rest = False
        self.duration: int = 0
        self.tie: list[str] = []
        # self.instrument = []
        # self.footnote = ""
        # self.level = ""
        self.voice = ""
        # self.note_type: str
        # self.dot: bool = False

        # self.stem: str
        # self.beam: str

        element_list = note.xpath(".//grace|.//cue")

        if element_list:
            pass
        else:
            element_list = note.xpath(".//pitch|.//unpitched|.//rest")

            match element_list[0].tag:
                case "pitch":
                    self.duration = note.find(".//duration").text
                # case "unpitched":
                case "rest":
                    self.duration = note.find(".//duration").text

    def set_pitch(self, pitch: XMLPitch):
        """TODO"""
        self.pitch = pitch

    def __str__(self) -> str:
        return f"Start: {self.start_tick}, Duration: {self.tick_duration}, Pitch: {self.pitch}"

    def __repr__(self) -> str:
        return f"Start: {self.start_tick}, Duration: {self.tick_duration}, Pitch: {self.pitch}"


class XMLBackup:
    def __init__(self, backup: LE._Element, tick: XMLTickCounter) -> None:
        self.start_tick = 0
        self.tick_count = 0


class XMLForward:
    def __init__(self, forward: LE._Element, tick: XMLTickCounter) -> None:
        pass


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
        self.wedge_type = wedge_type  # ENUM?
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

        # VVV Visual
        self.placement = ""


class XMLBarline:
    def __init__(self, barline: LE._Element, tick: XMLTickCounter):
        self.style = 0  # ENUM?
        self.repeat_direction = 0  # ENUM?


class XMLAttributes:
    def __init__(self):
        self.footnote = ""
        self.level = ""
        self.divisions = ""
        self.key = []
        self.time = []
        self.staves = ""
        self.part_symbol = ""
        self.instruments = ""
        self.clef = []
        self.staff_details = []
        self.measure_style = []


class XMLHarmony:
    def __init__(self):
        pass


class XMLFiguredBase:
    def __init__(self):
        pass


class XMLPrint:
    def __init__(self):
        pass


class XMLSound:
    def __init__(self):
        self.instrument_change = []
        self.midi_device = []
        self.midi_instrument = []
        self.play = []
        self.offset = ""
        self.swing = ""

        self.coda = ""
        self.dacapo = ""
        self.dalsegno = ""
        self.damper_pedal = ""
        self.divisions = ""
        self.dynamics = ""
        self.fine = ""
        self.forward_repeat = ""
        self.id = ""
        self.pizzicato = ""
        self.segno = ""
        self.soft_pedal = ""
        self.sostenuto_pedal = ""
        self.tempo = ""
        self.time_only = ""
        self.tocoda = ""


class XMLMeasure:
    def __init__(self, measure: LE._Element, tick: XMLTickCounter) -> None:
        self.start_tick = tick.get_tick()

        self.note_list: list[XMLNote] = []

        self.backup_list: list[XMLBackup] = []

        self.forward_list: list[XMLForward] = []

        self.direction_list: list[XMLDirection] = []

        self.attributes_list: list[XMLAttributes] = []

        # self.harmonty_list: list[XMLHarmony] = []
        # self.clef = []
        # self.print = []
        # self.sound = []
        self.barline_list = []
        # self.grouping = []
        # self.link = []
        # self.bookmark = []

        children_elements: list[LE._Element] = measure.getchildren()

        for element in children_elements:
            match element.tag:
                case "note":
                    new_note = XMLNote(element, tick)
                    self.note_list.append(new_note)
                case "backup":
                    new_backup = XMLBackup(element, tick)
                    self.backup_list.append(new_backup)
                case "forward":
                    new_forward = XMLForward(element, tick)
                    self.forward_list.append(new_forward)
                case "direction":
                    new_direction = XMLDirection(element, tick)
                    self.direction_list.append(new_direction)
                case "attributes":
                    new_attributes = XMLAttributes(element, tick)
                    self.attributes_list.append(new_attributes)
                case "barline":
                    new_barline = XMLBarline(element, tick)
                    self.barline_list.append(new_barline)

        self.number = measure.attrib["number"]
        # self.id = 0
        # self.implicit = False
        # self.non_controlling = False
        # self.text = ""
        # self.width = 0


class XMLScorePart:
    def __init__(self, score_part: LE._Element):
        """
        TODO
        """
        # self.identification = ""
        # self.part_link = ""
        self.part_name = score_part.find(".//part-name").text  # More info than this

        # self.part_name_display = ""

        element_list = score_part.xpath(".//part-abbreviation")
        if element_list:
            self.part_abbrev = element_list[0].text  # More info than this

        # self.part_abbreviation_display = ""

        # self.group = []

        # self.score_instrument = []
        # self.player = []
        # self.midi = []

        self.id: str = score_part.attrib["id"]


class XMLPart:
    def __init__(self, part: LE._Element) -> None:
        self.id = part.attrib["id"]

        self.measure_list: list[XMLMeasure] = []

        self.process_measures(part)

    def process_measures(self, part: LE._Element) -> None:
        measures = part.xpath(".//measure")

        tick = XMLTickCounter()

        for element in measures:
            new_measure = XMLMeasure(element, tick)
            self.measure_list.append(new_measure)


class XMLPartwise:
    def __init__(self, root: LE._Element):
        self.version = ""
        self.work = ""
        self.movement_number = ""
        self.movement_title = ""
        self.identificaiton = ""
        self.defaults = ""
        self.credits = ""

        self.part_list: list[XMLScorePart] = []

        self.parts: list[XMLPart] = []

        self.process_part_list(root)

        self.process_parts(root)

    def process_part_list(self, root: LE._Element) -> None:
        element_list = root.xpath(".//score-part")

        for element in element_list:
            new_score_part = XMLScorePart(element)
            self.part_list.append(new_score_part)

    def process_parts(self, root: LE._Element) -> None:
        element_list = root.xpath(".//part")

        for element in element_list:
            new_part = XMLPart(element)
            self.parts.append(new_part)


class MusicXML:
    def __init__(self, path: str) -> None:
        """
        Object that reads in a musicxml file and finds all the unique parts.

        param path: String path for the file that should be used.
        """
        self.file = LE.parse(path)
        """The parsed file."""
        root = self.file.getroot()

        self.note_start: int = 0
        self.note_duration: int = 0
        self.previous_duration: int = 0

        self.partwise = XMLPartwise(root)


if __name__ == "__main__":
    import os

    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_name = "test.musicxml"

    xml_file = f"{current_directory}/{file_name}"

    music_xml = MusicXML(xml_file)
