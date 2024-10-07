from solenoids import SolenoidIndex
from musicxml import NoteList

OUTSIDE_LOCATION = 1
INSIDE_LOCATION = 0


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

        self.possible_locations = set(
            self.key_map.playable_for_pitch(self.midi_pitches[0])
        )

    def add_pitch(self, new_midi_pitch: int) -> int:
        new_locations = self.key_map.playable_for_pitch(new_midi_pitch)
        temp_locations = set(self.possible_locations).intersection(new_locations)

        if temp_locations:
            self.possible_locations = temp_locations
            self.midi_pitches.append(new_midi_pitch)
            return INSIDE_LOCATION
        else:
            return OUTSIDE_LOCATION

    def __iter__(self) -> list[int]:
        return iter(self.midi_pitches)

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

    def __iter__(self) -> list[PlayableNote]:
        return iter(self.playable_list)

    def __str__(self) -> str:
        temp = ""
        for playable in self.playable_list:
            temp += str(playable) + "\n"
        return temp


class PlayableGroup:
    def __init__(self) -> None:
        self.playable_group: list[PlayableNote] = []
        self.possible_locations: set[int] = []

    def append(self, note: PlayableNote):

        new_locations = note.possible_locations

        temp_locations = set(self.possible_locations).intersection(new_locations)

        if temp_locations:
            self.possible_locations = temp_locations
            self.playable_group.append(note)
            return INSIDE_LOCATION

        elif self.possible_locations:
            return OUTSIDE_LOCATION
        else:
            self.possible_locations = note.possible_locations
            self.playable_group.append(note)
            return INSIDE_LOCATION


class PlayableGroupList:
    def __init__(self, key_map: SolenoidIndex, note_list: PlayableNoteList) -> None:
        self.key_map = key_map
        self.note_list = note_list
        self.group_list: list[PlayableGroup] = []
        self.find_groups()

    def find_groups(self) -> None:

        temp_group = PlayableGroup()

        for note in self.note_list:
            success = temp_group.append(note)

            if success == OUTSIDE_LOCATION:
                self.group_list.append(temp_group)
                temp_group = PlayableGroup()
                temp_group.append(note)

        self.group_list.append(temp_group)


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

    note_list = PlayableNoteList(key_map, first_staff)

    group_list = PlayableGroupList(key_map, note_list)

    print(group_list)


"""
Rough steps for compiling (Not for sure in this exact order):

Step 0: Ingest data and process it into format that can be used for Step 1 - 6

Step 1: Put notes into groups that can be played without the need for right/left movement

Step 2: Determine from each group which direction the hand will come from and go to.

Step 3: Based on the in/out direction of the hand what leniency can be granted while moving to the group

Step 4: Based on the in/out direction what movement should take place during the playing of the group

Step 5: Determine based on a cost function when a given movement should take place based on data from Step 2 - 4

Step 6: Use data to generate hardware playable file.



Possible group in/out:

Start/
    End # Single group. No need for additional processing
    Right/
        out overlap # Try to start and end as far right as the next group wants to go
        no overlap # Try to start and end as far right as possible
    Left/
        out overlap # Try to start and end as far left as possible
        no overlap # Try to start and end as far left as possible
Right/
    End # Last group. Only leniency movement needed
    Right/
        in overlap # Try to start as far right as the previous group wants to go and end as far right as possible
        out overlap # Try to start and end as far right as the next group wants to go
        in out overlap # Try to start as far right as the previous group wants to go and end as far right as the next group want to go
        no overlap # Try to start and end as far right as possible
    Left/
        in overlap # Try to start as far right as the previous group wants to go and end as far left as possible
        out overlap # Try to start as far right as possible and end as far left as the next group wants to go
        in out overlap # Try to start as far right as the previous group wants to go and end as far left as the next group want to go
        no overlap # Try to start as far right as possible and end as far left as possible
Left/
    End # Last group. Only leniency movement needed
    Right/
        in overlap # Try to start as far left was the previous group wants to go and end as far right as possible
        out overlap # Try to start as far left as possible and end as far right as the next group wants to go
        in out overlap # Try to start as far left as the previous group wants to go and end as far right as the next group want to go
        no overlap # Try to start as far left as possible and end as far right as possible
    Left/
        in overlap # Try to start as far left as the previous group wants to go and end as far left as possible
        out overlap # Try to start and end as far left as the next group want to go
        in out overlap # Try to start as far left as the previous group wants to go and end as far left as the next group want to go
        no overlap # Try to start and end as far left as possible

"""
