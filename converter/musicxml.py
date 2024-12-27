import lxml.etree as LE

NOTES_IN_OCTAVE = 12
BASE_OCTAVE_OFFSET = 1

MISSING_VOLUME = -1

# TODO Look for dynamics in measure
# TODO Ties and slurs
# TODO Turn


class XMLNote:
    def __init__(
        self,
        note_start: int,
        duration: int,
        midi_pitch: int,
        velocity: int,
        modifiers: list[str] = [],
    ) -> None:
        """
        Object that represents a single note/chord from an musicxml file.

        param note_start: An integer that represents the start time of the note(s) in terms of musicXML ticks.
        param duration: An integer that represents the total duration the note(s) in terms of musicXML ticks.
        param midi_pitch: An integer that represents the pitch of the note equivilent to the midi pitch number.
        param velocity: An integer that represents the volume of the note(s) similar to midi velocity.
        param modifiers: TODO
        """
        self.note_start = note_start
        """The number of musicxml ticks as an integer from the piece start to beginning to play this note."""
        self.duration = duration
        """The number of musicxml ticks as an integer from the start of the note to the end of the note."""
        self.midi_pitch = midi_pitch
        """
        The group of pitches that make up this note represented by 
        integer values equal to the midi representation.
        """
        self.velocity = velocity
        """The volume/velocity/force the note should be played with represented as an interger."""
        self.modifiers = modifiers
        """TODO"""

    def __str__(self) -> str:
        return f"Start: {self.note_start}, Duration: {self.duration}, Midi_Pitch: {self.midi_pitch}, Velocity: {self.velocity}"


class XMLNoteList:
    def __init__(self, part_id: str, staff_number: int) -> None:
        """
        A list of XMLNotes for a given part id and staff number.

        param part_id: The musicxml part id as a string.
        param staff_number: The musicxml staff number for a given part id as an integer.
        """
        self.notes: list[XMLNote] = []
        """List of XMLNotes for the part id for a specific staff number."""
        self.part_id = part_id
        """Musicxml part id."""
        self.staff_number = staff_number
        """Musicxml staff number."""

    def append(self, XMLNote) -> None:
        """Append a XMLNote to notes."""
        self.notes.append(XMLNote)

    def __str__(self) -> str:
        temp = ""
        for note in self.notes:
            temp += str(note) + "\n"
        return temp

    def __iter__(self):  # TODO Type hint?
        return iter(self.notes)


class PartInfo:
    def __init__(self, id: str, staff_count: int) -> None:
        """
        Object that stores all the information needed to identify the unique part.
        """
        self.id = id
        self.staff_count = staff_count


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
        self.parts = self.root.findall("part")
        """Each part under the root element."""
        self.part_ids = self.find_part_ids()
        """List of each unique part."""

    def find_part_ids(self) -> list[PartInfo]:
        """
        Based on the musicxml provided in the object find each unique part.

        return: Returns the unique parts as a list of PartInfos.
        """
        temp: list[str] = []
        partlist_element = self.root.find("part-list")
        part_list = partlist_element.findall(".//score-part")
        for part in part_list:
            part_id = part.attrib["id"]
            staff_count = self.find_staff_count(part_id)
            part_info = PartInfo(part_id, staff_count)
            temp.append(part_info)
        return temp

    def find_part(self, part_id: str) -> LE._Element:
        """Find the musicxml part associated with the given part id.

        param part_id: A string containing the part id of the desired part.

        return: Returns the xml element of the part.
        """
        part = self.root.find(f".//part[@id='{part_id}']")
        return part

    def find_staff_count(self, part_id: str) -> int:
        """
        Finds the total numberof staves for a given part id.

        param part_id: A string containing the part id of the desired part.

        return: Returns an interger value representing the total number of staves.
        """
        temp: list[str] = []
        matched_part = self.find_part(part_id)
        measures = matched_part.findall(".//note/staff")
        for item in measures:
            temp.append(item.text)
        temp = set(temp)
        staff_count = len(temp)
        if staff_count == 0:
            staff_count = 1
        return staff_count

    def us_per_division(self, part_id: str) -> None:
        """
        Determines the microseconds per musicxml division as an integer.

        param part_id: A string value for the part id.
        """
        matched_part = self.find_part(part_id)
        divisions = int(matched_part.find(".//divisions").text)
        beat_type = int(matched_part.find(".//beat-type").text)
        tempo_element = matched_part.find(".//*[@tempo]")

        if tempo_element is not None:
            tempo = int(tempo_element.attrib["tempo"])
        else:
            # TODO Randomish default if no tempo is defined
            tempo = 120

        quarters_per_beat = 4 / 4  # beat_type
        quarters_per_minute = tempo * quarters_per_beat
        divisions_per_minute = quarters_per_minute * divisions
        us_per_minute = 1e6 * 60
        self.us_per_div = int(us_per_minute / float(divisions_per_minute))

    def find_velocity(self, part_id: str) -> int:
        """TODO This assumes the entire part has the same velocity/volume which is not always true.
        Find the velocity/volume for a given part.

        param part_id: A string value for the part id.

        return: Returns an integer value of the musicxml volume.
        """
        partlist_element = self.root.find("part-list")
        part_list = partlist_element.findall(".//score-part")
        for item in part_list:
            if item.attrib["id"] == part_id:
                score_part = item
                part_velocity = float(score_part.find(".//volume").text)

                return part_velocity

        # TODO Maybe raise an exception. Ideally if volume is missing that can be selected by user.
        return MISSING_VOLUME

    def generate_note_list(self, part_info: PartInfo) -> list[XMLNoteList]:
        """
        For a given part_info generate a list of XMLNoteLists for each staff contained in a part.

        param part_info: A PartInfo object containing the part id and the number of staves for that part.

        return: Returns a list of XMLNoteList where each XMLNoteList is for an individual staff.
        """
        part = self.find_part(part_info.id)
        notes = list[LE._Element](part.xpath(".//note | .//backup"))
        notes_list: list[XMLNoteList] = []
        for i in range(0, part_info.staff_count):
            new_note_list = XMLNoteList(part_info.id, i + 1)
            notes_list.append(new_note_list)
        note_start = 0
        note_duration = 0
        velocity: int = self.find_velocity(part_info.id)
        for note in notes:
            prev_note_duration = note_duration
            note_duration = int(note.xpath(".//duration")[0].text)
            note_pitch = note.xpath(".//pitch")
            note_rest = note.xpath(".//rest")
            note_staff = note.xpath(".//staff")
            if len(note_staff) > 0:
                staff = int(note_staff[0].text)
            else:
                staff = 1

            # If the note has a pitch then it is actually a note.
            if len(note_pitch) > 0:
                # Find all the info to convert the note pitch to MIDI pitch.
                note_letter = note_pitch[0].xpath("step")[0].text
                note_octave = int(note_pitch[0].xpath("octave")[0].text)
                note_alter = note_pitch[0].xpath("alter")
                if len(note_alter) > 0:
                    note_alter = int(note_alter[0].text)
                else:
                    note_alter = 0
                note_midi = pitch_to_midi(note_letter, note_octave, note_alter)

                # Check if the note is part of a chord
                note_chord = note.xpath(".//chord")
                if len(note_chord) > 0:
                    note_start -= prev_note_duration

                    # Store all relavent info about the note.
                    new_XMLNote = XMLNote(
                        note_start, note_duration, note_midi, velocity
                    )
                    notes_list[staff - 1].append(new_XMLNote)  # HERE

                    note_start += prev_note_duration
                    note_duration = prev_note_duration

                else:
                    # Store all relavent info about the note.
                    new_XMLNote = XMLNote(
                        note_start, note_duration, note_midi, velocity
                    )
                    notes_list[staff - 1].append(new_XMLNote)  # HERE

                    note_start += note_duration

            # Rests don't need to be stored and only move the timing forward.
            elif len(note_rest) > 0:
                note_start += note_duration

            # A note that is neither a true note or rest should be a backup and need to
            # turn back the note_start counter.
            else:
                note_start -= note_duration

        return notes_list


def pitch_to_midi(letter: str, octave: int, alter: int) -> int:
    """
    Converts a string representation of a pitch to its midi equivilent.

    param letter: The letter of the pitch as a string.
    param octave: The octave of the pitch as an integer.
    param alter: An integer which represents if the note is a sharp or flat.
    """
    note_offset = ord(letter) - ord("C")
    octave_offset = (octave + BASE_OCTAVE_OFFSET) * NOTES_IN_OCTAVE

    if note_offset >= 0 and note_offset < 3:
        missing_half_step = 0
    elif note_offset >= 3:
        missing_half_step = 1
    else:
        missing_half_step = -13

    return ((note_offset * 2) - missing_half_step) + octave_offset + alter
