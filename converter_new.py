import lxml.etree as LE


NOTES_IN_OCTAVE = 12
BASE_OCTAVE_OFFSET = 1


class XMLNote:
    def __init__(
        self, note_start: int, duration: int, midi_pitch: int, modifiers: list[str] = []
    ) -> None:
        self.note_start = note_start
        self.duration = duration
        self.midi_pitch = midi_pitch
        self.modifiers = modifiers

    def __str__(self) -> str:
        return f"Start: {self.note_start}, Duration: {self.duration}, Midi_Pitch: {self.midi_pitch}"


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


def division_ms(divisions: int, tempo: int, beat_type: int) -> int:
    quarters_per_beat = 4 / beat_type
    quarters_per_minute = tempo * quarters_per_beat

    divisions_per_minute = quarters_per_minute * divisions

    us_per_minute = 1e6 * 60

    us_per_divistion = int(us_per_minute / float(divisions_per_minute))

    return us_per_divistion


file = LE.parse("test.musicxml")

root = file.getroot()

parts = root.findall("part")

partlist = root.find("part-list")

piano_part_id = partlist.find(".//*[part-name='Piano']").attrib["id"]

piano_part = root.findall(".//*[@id='" + piano_part_id + "']")[1]

piano_divisions = int(piano_part.find(".//divisions").text)

# piano_beats = piano_part.find(".//beats").text

piano_beat_type = int(piano_part.find(".//beat-type").text)

piano_tempo = piano_part.find(".//*[@tempo]")

if piano_tempo is not None:
    tempo = int(piano_tempo.attrib["tempo"])
else:
    # TODO Randomish default if no tempo is defined
    tempo = 120


us_per_division = division_ms(piano_divisions, tempo, piano_beat_type)

piano_notes: list[LE._Element] = piano_part.xpath(".//note | .//backup")

# print(piano_notes)

note_list: list[list] = []

note_start = 0

# TODO Add invalid value checking
for note in piano_notes:
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
    if len(note_pitch) > 0:
        note_letter = note_pitch[0].xpath("step")[0].text
        note_octave = int(note_pitch[0].xpath("octave")[0].text)
        note_alter = note_pitch[0].xpath("alter")
        if len(note_alter) > 0:
            note_alter = int(note_alter[0].text)
        else:
            note_alter = 0
        note_midi = pitch_to_midi(note_letter, note_octave, note_alter)
        new_XMLNote = XMLNote(note_start, note_duration, note_midi)
        note_list[staff - 1].append(new_XMLNote)
        note_start += note_duration
    elif len(note_rest) > 0:
        note_start += note_duration
    else:
        note_start -= note_duration


for items in note_list:
    print(
        "=================================================================================================="
    )
    for item in items:
        print(item)
