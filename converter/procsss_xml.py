from __future__ import annotations
from generated.musicxml import (
    ScorePartwise,
    ScorePart,
    Note,
    Backup,
    Forward,
    Direction,
    DirectionType,
    Dashes,
    StartStopContinue,
    Wedge,
    Attributes,
    WedgeType,
    Pitch,
)
from xsdata.formats.dataclass.parsers import XmlParser
from decimal import Decimal
from operator import itemgetter


class TaggedNote:
    def __init__(self, note: Note, tick: Decimal):
        self.note = note
        self.tick = tick


class TempoList:
    def __init__(self):
        self.tempo_list: list[tuple[Decimal]] = []

    def append(self, tempo: Decimal, tick: Decimal) -> None:
        self.tempo_list.append((tempo, tick))

    def tempo_at_tick(self, tick: Decimal) -> Decimal:
        tick_index = len([i for i in self.tempo_list if i[1] <= tick]) - 1

        self.sort()

        result = self.tempo_list[tick_index][0]

        return result

    def sort(self) -> None:
        self.tempo_list.sort(key=itemgetter(1))

    def combine(self, list_tempos: TempoList) -> None:
        temp_list = self.tempo_list + list_tempos.tempo_list
        self.tempo_list = list(dict.fromkeys(temp_list))


class DynamicList:
    def __init__(self):
        self.dynamic_list: list[tuple[Decimal]] = []

    def append(self, dynamic: Decimal, tick: Decimal) -> None:
        self.dynamic_list.append((dynamic, tick))

    def dynamic_at_tick(self, tick: Decimal) -> Decimal:
        tick_index = len([i for i in self.dynamic_list if i[1] <= tick]) - 1

        self.sort()

        result = self.dynamic_list[tick_index][0]

        return result

    def sort(self) -> None:
        self.dynamic_list.sort(key=itemgetter(1))

    def combine(self, list_tempos: DynamicList) -> None:
        temp_list = self.dynamic_list + list_tempos.dynamic_list
        self.dynamic_list = list(dict.fromkeys(temp_list))


def extract_direction_tempo(
    result_list: TempoList, direction: Direction, tick: Decimal
) -> None:
    if direction.sound is None:
        return
    elif direction.sound.tempo is None:
        return
    else:
        tempo = direction.sound.tempo
        result_list.append(tempo, tick)


def extract_tempo(tick_tagged_list: list[tuple]) -> TempoList:
    """"""
    tempo_list = TempoList()

    variation_list: list[tuple] = []

    for element in tick_tagged_list:
        if isinstance(element[0], Direction):
            extract_direction_tempo(tempo_list, element[0], element[1])

            for direction_type in element[0].direction_type:
                for choice in direction_type.choice:
                    if isinstance(choice, DirectionType.Words):
                        variation_list.append((choice.value, element[1]))

                    elif isinstance(choice, Dashes):
                        if choice.type_value == StartStopContinue.STOP:
                            variation_list.append(("stop", element[1]))

    for i in range(0, int(len(variation_list) / 2)):
        variation_start = variation_list.pop(0)
        variation_end = variation_list.pop(0)
        variation_type = variation_start[0]
        variation_start_tick = variation_start[1]
        variation_stop_tick = variation_end[1]
        variation_duration = variation_stop_tick - variation_start_tick

        start_tempo = tempo_list.tempo_at_tick(variation_start_tick)

        stop_tempo = tempo_list.tempo_at_tick(variation_stop_tick)

        if variation_type == "accel.":
            if start_tempo == stop_tempo:
                stop_tempo = Decimal(round((stop_tempo * 4 / 3)))
            tempo_difference = stop_tempo - start_tempo

        elif variation_type == "rit.":
            if start_tempo == stop_tempo:
                stop_tempo = Decimal(round((stop_tempo * 3 / 4)))
            tempo_difference = stop_tempo - start_tempo
        else:
            continue

        for i in range(0, int(variation_duration) + 1):
            tempo = round((i / (variation_duration)) * tempo_difference) + start_tempo
            tempo_list.append(tempo, variation_start_tick + i)

    return tempo_list


def extract_direction_dynamic(
    result_list: DynamicList, direction: Direction, tick: Decimal
) -> None:
    if direction.sound is None:
        return
    elif direction.sound.dynamics is None:
        return
    else:
        dynamics = direction.sound.dynamics
        result_list.append(dynamics, tick)


def extract_dynamics(tick_tagged_list: list[tuple]) -> DynamicList:
    dynamic_list = DynamicList()

    variation_list: list[tuple] = []

    for element in tick_tagged_list:
        if isinstance(element[0], Direction):
            extract_direction_dynamic(dynamic_list, element[0], element[1])

            for direction_type in element[0].direction_type:
                for choice in direction_type.choice:
                    if isinstance(choice, Wedge):
                        variation_list.append((choice.type_value, element[1]))

    for i in range(0, int(len(variation_list) / 2)):
        variation_start = variation_list.pop(0)
        variation_end = variation_list.pop(0)
        variation_type = variation_start[0]
        variation_start_tick = variation_start[1]
        variation_stop_tick = variation_end[1]
        variation_duration = variation_stop_tick - variation_start_tick

        start_dynamic = dynamic_list.dynamic_at_tick(variation_start_tick)

        stop_dynamic = dynamic_list.dynamic_at_tick(variation_stop_tick)

        if variation_type == WedgeType.CRESCENDO:
            if start_dynamic == stop_dynamic:
                stop_dynamic = Decimal(round((stop_dynamic * 4 / 3)))
            dynamic_difference = stop_dynamic - start_dynamic

        elif variation_type == WedgeType.DIMINUENDO:
            if start_dynamic == stop_dynamic:
                stop_dynamic = Decimal(round((stop_dynamic * 3 / 4)))
            dynamic_difference = stop_dynamic - start_dynamic
        for i in range(0, int(variation_duration) + 1):
            tempo = (
                round((i / (variation_duration)) * dynamic_difference) + start_dynamic
            )
            dynamic_list.append(tempo, variation_start_tick + i)

    return dynamic_list


def chord_check(note: Note) -> tuple[bool, Decimal]:
    """TODO"""

    result = any(isinstance(x, Note.Chord) for x in note.choice)

    return result


def find_note_duration(note: Note) -> Decimal:
    """TODO"""

    result = Decimal(0)

    for item in note.choice:
        if isinstance(item, Decimal):
            result = item

    return result


def tick_tag_note(
    current_tick: Decimal,
    note: Note,
    result_list: list[tuple],
    previous_note_dur: Decimal,
) -> Decimal:
    """TODO"""

    duration = find_note_duration(note)

    if chord_check(note):
        current_tick -= previous_note_dur
        result_list.pop()
        result_list.append((note, current_tick))
        result_tick = current_tick + previous_note_dur
        result_previous = previous_note_dur
    else:
        result_tick = current_tick + duration
        result_previous = duration

    return (result_tick, result_previous)


def tick_tag_measure(
    measure: ScorePartwise.Part.Measure, result_list: list[tuple], measure_tick: Decimal
) -> Decimal:
    """"""
    previous_note_dur = Decimal(0)

    current_tick = measure_tick

    for element in measure.choice:
        result_list.append((element, current_tick))

        if isinstance(element, Note):
            (current_tick, previous_note_dur) = tick_tag_note(
                current_tick,
                element,
                result_list,
                previous_note_dur,
            )

        elif isinstance(element, Backup):
            current_tick -= element.duration

        elif isinstance(element, Forward):
            current_tick += element.duration

    return current_tick


def tick_tag_part(part: ScorePartwise.Part) -> list[tuple]:
    """"""
    result_list = []

    current_tick: Decimal = 0

    for measure in part.measure:
        current_tick = tick_tag_measure(measure, result_list, current_tick)

    return result_list


def extract_pitch(note: Note) -> tuple[str, int, Decimal]:
    for item in note.choice:
        if isinstance(item, Pitch):
            step = str(item.step.value)
            octave: int = item.octave
            alter = item.alter

            if alter is None:
                alter = Decimal(0)

            return (step, octave, alter)

    raise ValueError("Note does not contain pitch")


class MusicPiece:
    def __init__(self, file: str) -> None:
        parser = XmlParser()

        self.music_piece = parser.parse(file, ScorePartwise)

        self.parts_list = self.find_part_list()
        self.parts = self.music_piece.part

        self.tagged_parts = self.tick_tag_parts()

        self.tempo_list = self.find_tempo_list()

    def find_part_list(self) -> list[ScorePart]:
        mixed_list = self.music_piece.part_list.part_group_or_score_part

        temp_list: list[ScorePart] = []

        for item in mixed_list:
            if isinstance(item, ScorePart):
                temp_list.append(item)

        return temp_list

    def tick_tag_parts(self) -> list[list[tuple]]:
        tick_tag_lists: list[list[tuple]] = []
        for part in self.parts:
            tick_tag_lists.append(tick_tag_part(part))

        return tick_tag_lists

    def find_tempo_list(self) -> TempoList:
        temp_list = TempoList()
        for part in self.tagged_parts:
            temp_list.combine(extract_tempo(part))

        return temp_list

    def find_dynamic_list(self, score_part: ScorePart) -> DynamicList:
        temp_list = DynamicList()

        part_index = 0

        for i, part in enumerate(self.parts):
            if part.id == score_part.id:
                part_index = i

        tagged_part = self.tagged_parts[part_index]

        temp_list.combine(extract_dynamics(tagged_part))

        return temp_list

    def tick_tag_notes(
        self, score_part: ScorePart, voice_list: list[str]
    ) -> list[TaggedNote]:
        tagged_note_list: list[TaggedNote] = []

        part_index = 0

        for i, part in enumerate(self.parts):
            if part.id == score_part.id:
                part_index = i

        tagged_part = self.tagged_parts[part_index]

        for item in tagged_part:
            if isinstance(item[0], Note):
                if item[0].voice in voice_list:
                    tagged_note = TaggedNote(item[0], item[1])
                    tagged_note_list.append(tagged_note)

        return tagged_note_list

    def part_divisions(self, score_part: ScorePart) -> Decimal:
        part_index = 0
        divisions: Decimal = 0

        for i, part in enumerate(self.parts):
            if part.id == score_part.id:
                part_index = i

        tagged_part = self.tagged_parts[part_index]

        for item in tagged_part:
            if isinstance(item[0], Attributes):
                if item[0].divisions:
                    divisions = item[0].divisions

        return divisions

    def find_staves(self, score_part: ScorePart) -> int:
        """TODO"""

        staff_count: list[int] = []

        for i, part in enumerate(self.parts):
            if part.id == score_part.id:
                part_index = i

        tagged_part = self.tagged_parts[part_index]

        for item in tagged_part:
            if isinstance(item[0], Note):
                if item[0].staff not in staff_count:
                    staff_count.append(item[0].staff)

        return len(staff_count)

    def find_voices(self, score_part: ScorePart) -> list[str]:
        """TODO"""

        voice_list: list[str] = []

        for i, part in enumerate(self.parts):
            if part.id == score_part.id:
                part_index = i

        tagged_part = self.tagged_parts[part_index]

        for item in tagged_part:
            if isinstance(item[0], Note):
                if item[0].voice not in voice_list:
                    voice_list.append(item[0].voice)

        return voice_list


if __name__ == "__main__":
    import os

    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_name = "test.musicxml"

    xml_file = f"{current_directory}/{file_name}"

    process_music = MusicPiece(xml_file)

    score_part = process_music.parts_list[0]

    print(process_music.part_divisions(score_part))

    dynamic_list = process_music.find_dynamic_list(score_part)

    print(process_music.tick_tag_notes(score_part, 1))
