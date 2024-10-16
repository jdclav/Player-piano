from solenoids import SolenoidIndex
from musicxml import NoteList

OUTSIDE_LOCATION = 1
INSIDE_LOCATION = 0

NO_DIRECTION = 0
LEFT_DIRECTION = 1
RIGHT_DIRECTION = 2
UNKNOWN_DIRECTION = 3


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

        self.default_location = min(self.possible_locations)

    def add_pitch(self, new_midi_pitch: int) -> int:
        new_locations = self.key_map.playable_for_pitch(new_midi_pitch)
        filtered_locations = set(filter(lambda item: item is not None, new_locations))
        temp_locations = set(self.possible_locations) & filtered_locations

        if temp_locations:
            self.possible_locations = temp_locations
            self.midi_pitches.append(new_midi_pitch)
            self.default_location = min(self.possible_locations)
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
        self.need_moves: list[int,] = []
        self.freed_moves: list[int] = []
        self.need_points: list[int, int] = []
        self.freed_points: list[int, int] = []

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

    def find_default_position(self) -> int:
        return min(self.possible_locations)

    def min_locations(self, direction: bool) -> list[int]:
        """
        Finds the minimum location for each playable note in order.
        """
        locations: list[int] = []

        for note in self.playable_group:
            locations.append(min(note.possible_locations))

        unique_locations = list(set(locations))

        unique_locations.sort(reverse=direction)

        return unique_locations

    def max_locations(self, direction: bool) -> list[int]:
        """
        Finds the maximum location for each playable note in order.
        """
        locations: list[int] = []

        for note in self.playable_group:
            locations.append(max(note.possible_locations))

        unique_locations = list(set(locations))

        unique_locations.sort(reverse=direction)

        return unique_locations

    def find_need_points(self) -> None:
        in_direction = self.movement_directions[0]

        self.need_moves = [0] * len(self.playable_group)

        if in_direction == NO_DIRECTION:
            return

        if in_direction == LEFT_DIRECTION:
            ordered_locations = self.min_locations(True)
            current_group = self.playable_group
            while len(ordered_locations) > 0 and len(current_group) > 0:
                target_location = ordered_locations.pop(0)
                for i, note in enumerate(current_group):
                    min_location = min(note.possible_locations)
                    if min_location == target_location:
                        self.need_points.append([i, target_location])
                        current_group = current_group[0:i]
                        break

        elif in_direction == RIGHT_DIRECTION:
            ordered_locations = self.max_locations(False)
            current_group = self.playable_group
            while len(ordered_locations) > 0 and len(current_group) > 0:
                target_location = ordered_locations.pop(0)
                for i, note in enumerate(current_group):
                    max_location = max(note.possible_locations)
                    if max_location == target_location:
                        self.need_points.append([i, target_location])
                        current_group = current_group[0:i]
                        break
            print("test")
        else:
            raise (TypeError("Direction no specified."))

    def find_freed_points(self) -> None:
        out_direction = self.movement_directions[1]

        self.freed_moves = [0] * len(self.playable_group)

        if out_direction == NO_DIRECTION:
            return

        if out_direction == LEFT_DIRECTION:
            ordered_locations = self.max_locations(True)
            current_group = list(reversed(self.playable_group))
            while len(ordered_locations) > 1 and len(current_group) > 1:
                target_location = ordered_locations.pop(0)
                for i, note in enumerate(current_group):
                    min_location = max(note.possible_locations)
                    if min_location == target_location:
                        self.freed_points.append([i, target_location])
                        current_group = current_group[0:i]
                        break

        elif out_direction == RIGHT_DIRECTION:
            ordered_locations = self.min_locations(False)
            current_group = list(reversed(self.playable_group))
            while len(ordered_locations) > 1 and len(current_group) > 1:
                target_location = ordered_locations.pop(0)
                for i, note in enumerate(current_group):
                    max_location = min(note.possible_locations)
                    if max_location == target_location:
                        self.freed_points.append([i, target_location])
                        current_group = current_group[0:i]
                        break
        else:
            raise (TypeError("Direction no specified."))


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

    for group in group_list.group_list:
        group.find_need_points()

    for group in group_list.group_list:
        group.find_freed_points()

    print(group_list)


"""
            minimum_first_note = min(self.playable_group[0].possible_locations)
            minimum_previous_note = min()
            first_move =

"""


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
