from solenoids import SolenoidIndex
from musicxml import NoteList


class PlayableNote:
    def __init__(
        self,
        key_map: SolenoidIndex,
        note_start: int,
        duration: int,
        midi_pitch: int,
        velocity: int,
    ) -> None:
        self.note_start = note_start
        self.duration = duration
        self.midi_pitches = [midi_pitch]
        self.velocity = velocity
        self.key_map = key_map

        self.possible_locations = self.key_map.playable_for_pitch(self.midi_pitches[0])

    def add_pitch(self, new_midi_pitch: int) -> int:
        self.midi_pitches.append(new_midi_pitch)

        new_locations = self.key_map.playable_for_pitch(new_midi_pitch)

        self.possible_locations = set(self.possible_locations).intersection(
            new_locations
        )

        if self.possible_locations:
            return 0
        else:
            return 1

    def __str__(self) -> str:
        temp_str = f"Start: {self.note_start}, "
        temp_str += f"Duration: {self.duration}, "
        temp_str += f"Midi_Pitches: {self.midi_pitches}, "
        temp_str += f"Velocity: {self.velocity}, "
        temp_str += f" Possible Locations: {self.possible_locations}"
        return temp_str


class PlayableNoteList:
    def __init__(self, key_map: SolenoidIndex, note_list: NoteList) -> None:
        self.key_map = key_map
        self.note_list = note_list
        self.playable_list: list[PlayableNote] = []
        self.process_list()

    def process_list(self):
        for note in self.note_list:
            if self.playable_list:
                previous_playable = self.playable_list[-1]
                if previous_playable.note_start == note.note_start:
                    previous_playable.add_pitch(note.midi_pitch)
                else:
                    temp_playable = PlayableNote(
                        self.key_map,
                        note.note_start,
                        note.duration,
                        note.midi_pitch,
                        note.velocity,
                    )

                    self.playable_list.append(temp_playable)
            else:
                temp_playable = PlayableNote(
                    self.key_map,
                    note.note_start,
                    note.duration,
                    note.midi_pitch,
                    note.velocity,
                )

                self.playable_list.append(temp_playable)

    def __str__(self) -> str:
        temp = ""
        for playable in self.playable_list:
            temp += str(playable) + "\n"
        return temp


if __name__ == "__main__":
    import os
    from constants import Constants
    from musicxml import MusicXML

    constants = Constants()

    key_map = SolenoidIndex(88, constants.first_88_key)

    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_name = "test.musicxml"

    xml_file = f"{current_directory}/{file_name}"

    music_xml = MusicXML(xml_file)

    first_part = music_xml.part_ids[1]

    first_staff = music_xml.generate_note_list(first_part)[0]

    test = PlayableNoteList(key_map, first_staff)

    print(test)
