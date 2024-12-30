import lxml.etree as LE


NOTES_IN_OCTAVE = 12
BASE_OCTAVE_OFFSET = 1

MISSING_VOLUME = -1

US_PER_MINUTE = 1e6 * 60

# TODO Look for dynamics in measure


class XMLNote:
    def __init__(
        self,
        note_start: int,
        duration: int,
        midi_pitch: int,
        velocity: int,
        us_per_tick: float,
        modifiers: list[str],
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
        self.us_per_tick = us_per_tick
        self.modifiers = modifiers
        """TODO"""

    def __str__(self) -> str:
        return f"Start: {self.note_start}, Duration: {self.duration}, Midi_Pitch: {self.midi_pitch}, Velocity: {self.velocity}"


class XMLRest:
    def __init__(
        self,
        rest_start: int,
        duration: int,
        us_per_tick: float,
        modifiers: list[str],
    ) -> None:
        """
        TODO
        """
        self.rest_start = rest_start

        self.duration = duration

        self.us_per_tick = us_per_tick

        self.modifiers = modifiers


class XMLDynamic:
    def __init__(
        self,
        dynamic_start: int,
        dynamic_velocity: float,
    ) -> None:
        """
        TODO
        """

        self.dynamic_start = dynamic_start

        self.dynamic_velocity = dynamic_velocity


class XMLTempo:
    def __init__(self, tempo_start: int, tempo_value: float):
        """
        TODO
        """

        self.tempo_start = tempo_start

        self.tempo_value = tempo_value


class PartInfo:
    def __init__(self, id: str, staff_count: int, divisions: int) -> None:
        """
        Object that stores all the information needed to identify the unique part.
        """
        self.id = id
        self.staff_count = staff_count
        self.divisions = divisions


class XMLNoteList:
    def __init__(self, part_info: PartInfo, staff_number: int) -> None:
        """
        A list of XMLNotes for a given part id and staff number.

        param part_id: The musicxml part id as a string.
        param staff_number: The musicxml staff number for a given part id as an integer.
        """
        self.notes: list[XMLNote] = []
        """List of XMLNotes for the part id for a specific staff number."""
        self.rests: list[XMLRest] = []
        """List of XMLRests for hte part id for a specific staff number."""
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
        self.note_lists: list[XMLNoteList] = []

        self.tempo_list: list[XMLTempo] = []

        self.dynamic_list: list[XMLDynamic] = []

        self.note_start: int = 0
        self.note_duration: int = 0

    def find_part_info(self) -> list[PartInfo]:
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
            part = self.find_part(part_id)
            divisions = int(part.xpath(".//divisions")[0].text)
            part_info = PartInfo(part_id, staff_count, divisions)
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

    def find_articulations(self, note: LE._Element, modifiers: list[str]):
        """
        TODO
        """
        note_accent: LE._Element = note.xpath(".//accent")
        note_tenuto: LE._Element = note.xpath(".//tenuto")
        note_staccato: LE._Element = note.xpath(".//staccato")

        if len(note_accent) > 0:
            modifiers.append("accent")

        if len(note_tenuto) > 0:
            modifiers.append("tenuto")

        if len(note_staccato) > 0:
            modifiers.append("staccato")

    def find_notations(self, note: LE._Element, modifiers: list[str]):
        """
        TODO
        """
        note_tie = note.xpath(".//tie")
        note_slur = note.xpath(".//slur")

        if len(note_tie) > 0:
            tie_end = note_tie[0].attrib["type"]
            modifiers.append(f"tie-{tie_end}")

        if len(note_slur) > 0:
            slur_end = note_slur[0].attrib["type"]
            modifiers.append(f"slur-{slur_end}")

    def process_note(
        self, part_info: PartInfo, note: LE._Element, tempo: float, velocity: float
    ) -> None:
        """
        Takes in a musicxml note and extracts the component pieces.

        param note: The xml element containing the note data.

        return: TODO
        """
        modifiers: list[str] = []

        prev_duration = self.note_duration

        self.note_duration = int(note.xpath(".//duration")[0].text)
        note_pitch = note.xpath(".//pitch")
        note_rest = note.xpath(".//rest")
        note_staff = note.xpath(".//staff")

        self.find_articulations(note, modifiers)
        self.find_notations(note, modifiers)
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
                self.note_duration -= prev_duration

                us_per_tick = self.us_per_division(tempo, part_info.divisions)
                # Store all relavent info about the note.
                new_XMLNote = XMLNote(
                    self.note_start,
                    self.note_duration,
                    note_midi,
                    velocity,
                    us_per_tick,
                    modifiers,
                )
                self.note_lists[staff - 1].append_note(new_XMLNote)  # HERE

                self.note_start += prev_duration
                self.note_duration = prev_duration

            else:
                # Store all relavent info about the note.
                us_per_tick = self.us_per_division(tempo, part_info.divisions)
                new_XMLNote = XMLNote(
                    self.note_start,
                    self.note_duration,
                    note_midi,
                    velocity,
                    us_per_tick,
                    modifiers,
                )
                self.note_lists[staff - 1].append_note(new_XMLNote)  # HERE

                self.note_start += self.note_duration

        # Rests don't need to be stored and only move the timing forward.
        elif len(note_rest) > 0:
            us_per_tick = self.us_per_division(tempo, part_info.divisions)
            new_XMLRest = XMLRest(self.note_start, self.note_duration, us_per_tick, [])
            self.note_lists[staff - 1].append_rest(new_XMLRest)
            self.note_start += self.note_duration

    def process_backup(self, backup: LE._Element) -> int:
        """
        Takes in a musicxml backup and extracts the backup duration.

        param backup: The xml element containing the backup data.

        return: An integer value representing the duration of the backup.
        """
        note_duration = int(backup.xpath(".//duration")[0].text)

        return note_duration

    def process_direction(
        self,
        direction: LE._Element,
        current_tick: int,
    ) -> None:
        """
        Takes in a musicxml direction and extracts the component pieces.

        param direction: The xml element containing the direction data.

        return: A tuple of floats containing the new tempo and/or dynamic.
        """

        direction_type = direction.xpath(".//direction-type")[0]
        dynamic_element = direction_type.xpath(".//dynamics")
        metronome_element = direction_type.xpath(".//metronome")
        wedge_element = direction_type.xpath(".//wedge")

        if len(dynamic_element) > 0:
            sound_element = direction.xpath(".//sound")[0]
            velocity = float(sound_element.attrib["dynamics"])
            new_dynamic = XMLDynamic(current_tick, velocity)
            self.dynamic_list.append(new_dynamic)

        elif len(metronome_element) > 0:
            sound_element = direction.xpath(".//sound")[0]
            tempo = float(sound_element.attrib["tempo"])
            new_tempo = XMLTempo(current_tick, tempo)
            self.tempo_list.append(new_tempo)

        elif len(wedge_element) > 0:
            """TODO"""

    def us_per_division(self, tempo: float, divisions: int) -> float:
        """
        Determines the microseconds per musicxml division as an integer.

        param part_id: A string value for the part id.
        """

        divisions_per_minute = tempo * divisions

        return float(US_PER_MINUTE / float(divisions_per_minute))

    def generate_note_list(self, part_info: PartInfo) -> None:
        """TODO Break this function up
        For a given part_info generate a list of XMLNoteLists for each staff contained in a part.

        param part_info: A PartInfo object containing the part id and the number of staves for that part.

        return: Returns a list of XMLNoteList where each XMLNoteList is for an individual staff.
        """
        part: LE._Element = self.find_part(part_info.id)

        measure_elements = list[LE._Element](
            part.xpath(".//note | .//backup | .//direction")
        )

        for i in range(0, part_info.staff_count):
            new_note_list = XMLNoteList(part_info.id, i + 1)
            self.note_lists.append(new_note_list)

        velocity: int = self.find_velocity(part_info.id)
        tempo: float = 0

        for element in measure_elements:
            if element.tag == "note":
                self.process_note(part_info, element, tempo, velocity)

            elif element.tag == "backup":
                self.note_start -= self.process_backup(element)

            elif element.tag == "direction":
                (tempo, velocity) = self.process_direction(element, tempo, velocity)


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


if __name__ == "__main__":
    import os

    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_name = "test.musicxml"

    xml_file = f"{current_directory}/{file_name}"

    music_xml = MusicXML(xml_file)

    first_part = music_xml.part_info[0]

    music_xml.generate_note_list(first_part)

    print(music_xml.note_lists)
