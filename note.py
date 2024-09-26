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


class NoteList:
    def __init__(self) -> None:
        notes: list[XMLNote] = []


class MusicXML:
    def __init__(self, path: str) -> None:
        self.file = LE.parse(path)
        self.root = file.getroot()
        self.parts = self.root.findall("part")
        self.part_ids: list[str] = self.find_part_ids

    def find_part_ids(self) -> list[str]:
        temp: list[str] = []
        partlist_element = self.root.find("part-list")
        part_list = partlist_element.findall(".//score-part")
        for item in part_list:
            temp.append(item.attrib["id"])

    def find_staff_count(self, part_id: str) -> int:
        temp: list[str] = []
        matched_part = root.xpath(".//part[@id='" + part_id + "']")[0]
        measures = matched_part.findall(".//note/staff")
        for item in measures:
            temp.append(item.text)
        temp = set(temp)
        return len(temp)

    def division_ms(divisions: int, tempo: int, beat_type: int) -> int:
        quarters_per_beat = 4 / beat_type
        quarters_per_minute = tempo * quarters_per_beat
        divisions_per_minute = quarters_per_minute * divisions
        us_per_minute = 1e6 * 60
        us_per_divistion = int(us_per_minute / float(divisions_per_minute))
        return us_per_divistion

    def us_per_division(self, part_id: str) -> None:
        self.piano_part = root.findall(".//*[@id='" + part_id + "']")[1]
        piano_divisions = int(self.piano_part.find(".//divisions").text)
        piano_beat_type = int(piano_part.find(".//beat-type").text)
        piano_tempo = piano_part.find(".//*[@tempo]")

        if piano_tempo is not None:
            tempo = int(piano_tempo.attrib["tempo"])
        else:
            # TODO Randomish default if no tempo is defined
            tempo = 120

        self.us_per_div = self.division_ms(piano_divisions, tempo, piano_beat_type)


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


piano_notes: list[LE._Element] = piano_part.xpath(".//note | .//backup")

# print(piano_notes)

note_list: list[list] = []

note_start = 0

piano_measures  = piano_part.xpath(".//measure")

measure_count = len(piano_measures)

note_duration = 0

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
        if(len(note_chord) > 0):
            note_start -= prev_note_duration

            # Store all relavent info about the note.
            new_XMLNote = XMLNote(note_start, note_duration, note_midi)
            note_list[staff - 1].append(new_XMLNote)

            note_start += prev_note_duration
            note_duration = prev_note_duration
            #pass
            
        else:
            #pass

            # Store all relavent info about the note.
            new_XMLNote = XMLNote(note_start, note_duration, note_midi)
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

#These are verifications. They should calculate the numbers and use as pass fail
print(piano_divisions * 4) 
print((note_start + 72)/measure_count)