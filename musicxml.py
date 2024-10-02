import os
import lxml.etree as LE


NOTES_IN_OCTAVE = 12
BASE_OCTAVE_OFFSET = 1

MISSING_VOLUME = -1


class XMLNote:
    def __init__(
        self,
        note_start: int,
        duration: int,
        midi_pitch: int,
        velocity: int,
        modifiers: list[str] = [],
    ) -> None:
        self.note_start = note_start
        self.duration = duration
        self.midi_pitch = midi_pitch
        self.modifiers = modifiers
        self.velocity = velocity

    def __str__(self) -> str:
        return f"Start: {self.note_start}, Duration: {self.duration}, Midi_Pitch: {self.midi_pitch}, Velocity: {self.velocity}"


class NoteList:
    def __init__(self, part_id: str, staff_number: int) -> None:
        self.notes: list[XMLNote] = []
        self.part_id = part_id
        self.staff_number = staff_number

    def append(self, XMLNote) -> None:
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
        self.id = id
        self.staff_count = staff_count


class MusicXML:
    def __init__(self, path: str) -> None:
        self.file = LE.parse(path)
        self.root = self.file.getroot()
        self.parts = self.root.findall("part")
        self.part_ids = self.find_part_ids()

    def find_part_ids(self) -> list[PartInfo]:
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
        part = self.root.find(f".//part[@id='{part_id}']")
        return part

    def find_staff_count(self, part_id: str) -> int:
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

    def division_ms(divisions: int, tempo: int, beat_type: int) -> int:
        quarters_per_beat = 4 / beat_type
        quarters_per_minute = tempo * quarters_per_beat
        divisions_per_minute = quarters_per_minute * divisions
        us_per_minute = 1e6 * 60
        us_per_divistion = int(us_per_minute / float(divisions_per_minute))
        return us_per_divistion

    def us_per_division(self, part_id: str) -> None:
        part = root.findall(".//*[@id='" + part_id + "']")[1]
        divisions = int(part.find(".//divisions").text)
        beat_type = int(part.find(".//beat-type").text)
        tempo_element = piano_part.find(".//*[@tempo]")

        if tempo_element is not None:
            tempo = int(tempo_element.attrib["tempo"])
        else:
            # TODO Randomish default if no tempo is defined
            tempo = 120

        self.us_per_div = self.division_ms(divisions, tempo, beat_type)

    def find_velocity(self, part_id: str) -> int:
        partlist_element = self.root.find("part-list")
        part_list = partlist_element.findall(".//score-part")
        for item in part_list:
            if item.attrib["id"] == part_id:
                score_part = item
                part_velocity = int(score_part.find(".//volume").text)

                return part_velocity

        # TODO Maybe raise an exception. Ideally if volume is missing that can be selected by user.
        return MISSING_VOLUME

    def generate_note_list(self, part_info: PartInfo) -> list[NoteList]:
        part = self.find_part(part_info.id)
        notes = list[LE._Element](part.xpath(".//note | .//backup"))
        notes_list: list[NoteList] = []
        for i in range(0, part_info.staff_count):
            new_note_list = NoteList(part_info.id, i + 1)
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
    file = LE.parse("test.musicxml")
    root = file.getroot()
    parts = root.findall("part")
    partlist = root.find("part-list")
    part_list = partlist.findall(".//score-part")
    part_ids = []
    for item in part_list:
        part_ids.append(item.attrib["id"])
    piano_part_id = partlist.find(".//*[part-name='Piano']").attrib["id"]
    test = root.findall(".//*[@id='" + piano_part_id + "']")
    piano_part = root.xpath(".//part[@id='" + piano_part_id + "']")[0]
    piano_divisions = int(piano_part.find(".//divisions").text)
    piano_beats = piano_part.find(".//beats").text
    piano_beat_type = int(piano_part.find(".//beat-type").text)
    piano_tempo = piano_part.find(".//*[@tempo]")
    if piano_tempo is not None:
        tempo = int(piano_tempo.attrib["tempo"])
    else:
        # TODO Randomish default if no tempo is defined
        tempo = 120
    us_per_div = MusicXML.division_ms(piano_divisions, tempo, piano_beat_type)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    piano_notes: list[LE._Element] = piano_part.xpath(".//note | .//backup")
    note_list: list[list] = []  # Better way?
    note_start = 0
    note_duration = 0

    # Only for verification
    piano_measures = piano_part.xpath(".//measure")
    measure_count = len(piano_measures)

    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_name = "test.musicxml"
    xml_file = f"{current_directory}/{file_name}"
    music_xml = MusicXML(xml_file)
    velocity: int = music_xml.find_velocity(piano_part_id)

    # TODO Add invalid value checking
    for note in piano_notes:
        prev_note_duration = note_duration

        # TEMP Check if note is on an existing Staff. Add new list if staff is unique
        note_staff = note.xpath(".//staff")
        if len(note_staff) > 0:
            staff = int(note_staff[0].text)
        else:
            staff = 1
        while len(note_list) < staff:
            note_list.append([])

        note_duration = int(note.xpath(".//duration")[0].text)

        note_pitch = note.xpath(".//pitch")
        note_rest = note.xpath(".//rest")

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
                new_XMLNote = XMLNote(note_start, note_duration, note_midi, velocity)
                note_list[staff - 1].append(new_XMLNote)

                note_start += prev_note_duration
                note_duration = prev_note_duration
                # pass

            else:
                # pass

                # Store all relavent info about the note.
                new_XMLNote = XMLNote(note_start, note_duration, note_midi, velocity)
                note_list[staff - 1].append(new_XMLNote)

                note_start += note_duration

        # Rests don't need to be stored and only move the timing forward.
        elif len(note_rest) > 0:
            note_start += note_duration

        # A note that is neither a true note or rest should be a backup and need to
        # turn back the note_start counter.
        else:
            note_start -= note_duration

    for items in note_list:
        print(
            "=================================================================================================="
        )
        for item in items:
            print(item)

    # TODO These are verifications. They should calculate the numbers and use as pass fail
    print(piano_divisions * 4)
    print((note_start + 72) / measure_count)
