from solenoids import SolenoidIndex
from musicxml import NoteList

OUTSIDE_LOCATION = 1
INSIDE_LOCATION = 0

NO_DIRECTION = 0
LEFT_DIRECTION = 1
RIGHT_DIRECTION = 2
UNKNOWN_DIRECTION = 3

NO_OVERLAP = 0
YES_OVERLAP = 1
UNKNOWN_OVERLAP = 2


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

        new_locations = self.key_map.playable_for_pitch(midi_pitch)

        self.possible_locations = set(
            filter(lambda item: item is not None, new_locations)
        )

    def add_pitch(self, new_midi_pitch: int) -> int:
        new_locations = self.key_map.playable_for_pitch(new_midi_pitch)
        filtered_locations = set(filter(lambda item: item is not None, new_locations))
        temp_locations = set(self.possible_locations) & filtered_locations

        if temp_locations:
            self.possible_locations = temp_locations
            self.midi_pitches.append(new_midi_pitch)
            return INSIDE_LOCATION
        else:
            return OUTSIDE_LOCATION

    def highest_position(self) -> int:
        """
        Finds the furthest right the hand can be posistioned and still play every pitch

        return: Integer value that represent hand position.
        """
        return min(self.possible_locations)

    def __iter__(self) -> list[int]:
        return iter(self.midi_pitches)

    def __str__(self) -> str:
        temp_str = f"Start: {self.note_start}, "
        temp_str += f"Duration: {self.duration}, "
        temp_str += f"Midi_Pitches: {self.midi_pitches}, "
        temp_str += f"Velocity: {self.velocity}, "
        temp_str += f"Possible Locations: {self.possible_locations}"
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
        self.movement_directions: list[int] = [UNKNOWN_DIRECTION, UNKNOWN_DIRECTION]
        """
        Contains two values. 
        The direction the previous group was and the direction the next group will be.
        0: No group. This is be used for the beginning and ending values
        1: Group to the left.
        2: Group to the right.
        3: Not yet assigned.
        """
        self.movement_overlap: list[int] = [UNKNOWN_OVERLAP, UNKNOWN_OVERLAP]
        self.group_distance: list[int] = [0, 0]
        self.yields: list[int] = []

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

    def set_in_direction(self, direction: int) -> None:
        self.movement_directions[0] = direction

    def set_out_direction(self, direction: int) -> None:
        self.movement_directions[1] = direction

    def set_in_overlap(self, overlap: int) -> None:
        self.movement_overlap[0] = overlap

    def set_out_overlap(self, overlap: int) -> None:
        self.movement_overlap[1] = overlap

    def set_in_distance(self, distance: int) -> None:
        self.group_distance[0] = distance

    def set_out_distance(self, distance: int) -> None:
        self.group_distance[1] = distance

    def find_default_position(self) -> int:
        return min(self.possible_locations)

    def sorted_pitches(self) -> list[int]:
        all_pitches = [pitch for note in self.playable_group for pitch in note]
        each_unique_pitch = set(all_pitches)
        return sorted(each_unique_pitch)

    def find_in_yield(self) -> None:
        in_direction = self.movement_directions[0]
        in_overlap = self.movement_overlap[0]

        if in_direction == NO_DIRECTION:
            self.yields = [0] * len(self.playable_group)
            return

        ordered_pitches = self.sorted_pitches()

        if in_direction == LEFT_DIRECTION:

            pass

    def find_out_yield(self) -> None:
        out_direction = self.movement_directions[1]
        out_overlap = self.movement_overlap[1]
        pass


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

    def find_directions(self) -> None:
        previous_group: PlayableGroup = PlayableGroup()
        groups = self.group_list

        for i in range(len(groups)):
            current_group = groups[i]
            # Compare groups starting after the first
            if i != 0:
                previous_low_note = min(previous_group.playable_group[0])
                current_low_note = min(current_group.playable_group[0])

                if previous_low_note < current_low_note:
                    previous_group.set_out_direction(RIGHT_DIRECTION)
                    current_group.set_in_direction(LEFT_DIRECTION)
                else:
                    previous_group.set_out_direction(LEFT_DIRECTION)
                    current_group.set_in_direction(RIGHT_DIRECTION)

                if i == (len(groups) - 1):
                    current_group.set_out_direction(NO_DIRECTION)

            elif i == 0:
                current_group.set_in_direction(NO_DIRECTION)

            previous_group = groups[i]

    def find_overlap(self) -> None:
        previous_group = PlayableGroup()
        groups = self.group_list

        for i in range(len(groups)):
            current_group = groups[i]
            # Compare groups starting after the first
            if i != 0:
                previous_locations = previous_group.possible_locations
                current_locations = current_group.possible_locations

                temp_locations = set(previous_locations).intersection(current_locations)

                if temp_locations:
                    previous_group.set_out_overlap(YES_OVERLAP)
                    current_group.set_in_overlap(YES_OVERLAP)
                else:
                    previous_group.set_out_overlap(NO_OVERLAP)
                    current_group.set_in_overlap(NO_OVERLAP)

                if i == (len(groups) - 1):
                    current_group.set_out_overlap(NO_OVERLAP)

            elif i == 0:
                current_group.set_in_overlap(NO_OVERLAP)

            previous_group = groups[i]

    def find_group_distance(self) -> None:
        """
        Find the total distance needed to travel from the last group and
        to the next group for each Playable Group
        """
        previous_group = PlayableGroup()
        previous_location: int = 0
        for i, group in enumerate(self.group_list):
            current_location = group.find_default_position()
            if i != 0:
                distance = current_location - previous_location
                group.set_in_distance(distance)
                previous_group.set_out_distance(distance)
                if i == (len(self.group_list) - 1):
                    group.set_out_distance(0)
            else:
                group.set_in_distance(0)

            previous_group = group
            previous_location = current_location

        pass


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

    group_list.find_directions()

    group_list.find_overlap()

    group_list.find_group_distance()

    group_list.group_list[1].find_in_yield()

    print(group_list)


"""
Rough steps for compiling (Not for sure in this exact order):

Step 0: Ingest data and process it into format that can be used for Step 1 - 6 # Working example done

Step 1: Put notes into groups that can be played without the need for right/left movement

Step 2: Determine from each group which direction the hand will come from and go to as well as if the groups overlap

Step 3: Based on the in/out direction of the hand what leniency can be granted while moving to the group

Step 4: Based on the in/out direction what movement should take place during the playing of the group

Step 5: Determine based on a cost function when a given movement should take place based on data from Step 2 - 4

Step 6: Use data to generate hardware playable file.



Possible group in/out:

Start/
    End # Single group. No need for additional processing
    Right/
        out overlap # start and end as far right as the next group desires
        no overlap # start and end as far right as possible
    Left/
        out overlap # start and end as far left as possible
        no overlap # start and end as far left as possible
Right/
    End # Last group. Only leniency movement needed
    Right/
        in overlap # start as far right as the previous group desires, end as far right as possible
        out overlap # start and end as far right as the next group desires
        in out overlap # start as far right as the previous group desires, end as far right as the next group want to go
        no overlap # start and end as far right as possible
    Left/
        in overlap # start as far right as the previous group desires, end as far left as possible
        out overlap # start as far right as possible, end as far left as the next group desires
        in out overlap # start as far right as the previous group desires, end as far left as the next group want to go
        no overlap # start as far right as possible, end as far left as possible
Left/
    End # Last group. Only leniency movement needed
    Right/
        in overlap # start as far left was the previous group desires, end as far right as possible
        out overlap # start as far left as possible, end as far right as the next group desires
        in out overlap # start as far left as the previous group desires, end as far right as the next group want to go
        no overlap # start as far left as possible, end as far right as possible
    Left/
        in overlap # start as far left as the previous group desires, end as far left as possible
        out overlap # start and end as far left as the next group want to go
        in out overlap # start as far left as the previous group desires, end as far left as the next group want to go
        no overlap # start and end as far left as possible

"""
