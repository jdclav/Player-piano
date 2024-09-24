import lxml
import lxml.etree


class XMLNote:
    def __init__(
        self, note_start: int, duration: int, pitch: int, modifiers: list[str] = []
    ) -> None:
        self.note_start = note_start
        self.duration = duration
        self.pitch = pitch
        self.modifiers = modifiers


file = lxml.etree.parse("test.musicxml")

root = file.getroot()

parts = root.findall("part")


partlist = root.find("part-list")

piano_part_id = partlist.find(".//*[part-name='Piano']").attrib["id"]

piano_part = root.findall(".//*[@id='" + piano_part_id + "']")[1]

piano_divisions = piano_part.find(".//divisions").text

# piano_beats = piano_part.find(".//beats").text

# piano_beat_type = piano_part.find(".//beat-type").text

piano_notes = piano_part.xpath(".//note | .//backup")

# print(piano_notes)

note_list = []

note_start = 0

for note in piano_notes:
    note_duration = int(note.find(".//duration").text)

    note_pitch = note.find(".//pitch")
    note_rest = note.find(".//rest")

    if note_pitch is not None:
        note_letter = note_pitch.find("step").text
        note_octave = note_pitch.find("octave").text
        note_alter = note_pitch.find("alter")
        if note_alter is not None:
            note_alter = note_alter.text
    elif note_rest is not None:
        note_pitch = -1

    # Last
    note_start += int(note_duration)
