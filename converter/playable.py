from solenoids import SolenoidIndex
from musicxml import XMLNoteList

# TODO change to enum
OUTSIDE_LOCATION = 1
INSIDE_LOCATION = 0

# TODO change to enum
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
        """
        Holds all the information for a single playable set of notes. This could be a single key or a chord.
        Only contains a single start time and total duration so any keys played with a different start or duration
        must be held in a different instance.

        param key_map: A SolenoidIndex object that holds the mapping between midi pitch, key location, and valid
                       hand positions for a giving pitch.
        param note_start: An integer that represents the start time of the note(s) in terms of musicXML ticks.
        param duration: An integer that represents the total duration the note(s) in terms of musicXML ticks.
        param midi_pitch: An integer that represents the pitch of the note equivilent to the midi pitch number.
        param velocity: An integer that represents the volume of the note(s) similar to midi velocity.
        """
        self.note_start = note_start
        """The number of musicxml ticks as an integer from the piece start to beginning to play this note."""
        self.duration = duration
        """The number of musicxml ticks as an integer from the start of the note to the end of the note."""
        self.midi_pitches = [midi_pitch]
        """
        The group of pitches that make up this note represented by 
        integer values equal to the midi representation.
        """
        self.velocity = velocity
        """The volume/velocity/force the note should be played with represented as an interger."""
        self.key_map = key_map
        """
        A SolenoidIndex object that holds the mapping between midi pitch, key location, and valid
        hand positions for a giving pitch.
        """

        new_locations = self.key_map.playable_for_pitch(midi_pitch)
        self.possible_locations = set(
            filter(lambda item: item is not None, new_locations)
        )
        """A set that contains every valid location for the hand that allows this note to be played."""

        self.default_location = min(self.possible_locations)
        """The integer value used to represent the location of this note."""

    def add_pitch(self, new_midi_pitch: int) -> int:
        """
        Adds an additional pitch to the note. If the start, duration, and velocity are the same seperate pitches should
        be stored together in the PlayableNote using this function. If the pitch cannot be played at the same time
        as each currently stored note then do not add the note and return 1 else return 0.

        param new_midi_pitch: An integer that represents the pitch of the note equivilent to the midi pitch number
                              that will be added to the PlayableNote.
        """
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

    def max_position(self) -> int:
        """
        Returns the maximum position for this PlayableNote.

        return: Integer that represents the maximum possible_location.
        """
        return max(self.possible_locations)

    def min_position(self) -> int:
        """
        Returns the minimum position for this PlayableNote.

        return: Integer that represents the minimum possible_location.
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

    def __repr__(self) -> str:
        return f"{self.note_start}, {self.duration}, {self.midi_pitches}, {self.velocity, {self.possible_locations}}"


class PlayableNoteList:
    def __init__(self, key_map: SolenoidIndex, note_list: XMLNoteList) -> None:
        """
        Takes in a XMLNoteList object and converts it to a list of PlayableNotes. PlayableNotes combine same time notes
        to chords.

        param key_map: A SolenoidIndex object that holds the mapping between midi pitch, key location, and valid
                       hand positions for a giving pitch.
        param note_list: A XMLNoteList object containing each note for a particular staff of a musicxml part.
        """
        self.key_map = key_map
        """
        A SolenoidIndex object that holds the mapping between midi pitch, key location, and valid 
        hand positions for a giving pitch.
        """
        self.playable_list: list[PlayableNote] = []
        """The list of every note in the XMLNoteList in the form of PlayableNotes."""

        self.process_list(note_list)

    def process_list(self, note_list: XMLNoteList) -> None:
        """
        Processes the note_list into a list of PlayableNotes.

        param note_list: A XMLNoteList object containing each note for a particular staff of a musicxml part.
        """
        for note in note_list:
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

    def __repr__(self) -> str:
        temp = ""
        for playable in self.playable_list:
            temp += repr(playable) + "\n"
        return temp


class PlayableGroup:
    def __init__(self) -> None:
        """
        Represents a group of PlayableNotes that can be played without any hand movement.
        """
        self.playable_group: list[PlayableNote] = []
        """A list of Playable notes that can be played without any hand movement."""
        self.possible_locations: set[int] = []
        """Set of values that represent each possible location of hand location for this group."""
        self.movement_directions: list[int] = [UNKNOWN_DIRECTION, UNKNOWN_DIRECTION]
        """
        Contains two values. 
        The direction the previous group was and the direction the next group will be.
        0: No group. This is be used for the beginning and ending values
        1: Group to the left.
        2: Group to the right.
        3: Not yet assigned.
        """
        self.absolute_need: int = 0
        """The total moves needed from a previous group to this group."""
        self.absolute_freed: int = 0
        """The total moves that can be freed in this group to the next group."""
        self.moves: list[int] = []
        """
        For each item in the playable_group this will have a value to represent the total movement 
        that takes place after playing the note at the same index.
        """
        self.need_points: list[int, int] = []
        """
        Every location that movement need to take place from the previous group to allow 
        each note to be playable and the number of keys that need to be moved before 
        playing the current note.
        """
        self.freed_points: list[int, int] = []
        """
        Every location that movement can take place to get closer to the next group and 
        the number of keys that can be moved after the current note is played.
        """

    def append(self, note: PlayableNote) -> int:
        """
        Attempt to add a note to the current group. If the note cannot be played without
        movement in the current group.

        param note: A playable note that is intended to be added to the group."

        return: An interger value that represents whether the note can be added to the
        current group.
        """
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

    def append_move(self, move_value: int) -> None:
        self.moves.append(move_value)

    def set_in_direction(self, direction: int) -> None:
        """
        Set the value for the direction from which the group will be entered from.

        param direction: Integer value that represents the direction.
        """
        self.movement_directions[0] = direction

    def set_out_direction(self, direction: int) -> None:
        """
        Set the value for the direction from which the group will exit from.

        param direction: Integer value that represents the direction.
        """
        self.movement_directions[1] = direction

    def set_absolute_need(self, distance: int) -> None:
        """
        Set the value for the absolute movement needed to get to this group from
        the previous.

        param distance: An integer value that represents distance in keys.
        """
        self.absolute_need = distance

    def set_absolute_freed(self, distance: int) -> None:
        """
        Set the value for the absolute movement this group can perform to the next group

        param distance: An integer value that represents distance in keys.
        """
        self.absolute_freed = distance

    def first_need_points(self, last_note: PlayableNote) -> None:
        """
        Add the first need point based on the last note of the previous group.

        param last_note: A PlayableNote that is the last note of the previous group.
        """
        self.need_points.insert(0, [0, 0])

    def last_freed_points(self, next_note: PlayableNote) -> None:
        """TODO Does nothing useful atm.
        Add the last freed point based on the first note of the next group.

        param last_note: A PlayableNote that is the first note of the next group.
        """
        self.freed_points.append([0, 0])

    def find_default_position(self) -> int:
        """Is this used?"""
        return min(self.possible_locations)

    def min_locations(self, direction: bool) -> list[int]:
        """
        Finds the minimum location for each playable note in either sort direction based
        on direction parameter.

        param direction: The direction to sort the returned list. False ascending and
        true descending

        return: List of integer values of each minimum location sorted based on
        direction state.
        """
        locations: list[int] = []

        for note in self.playable_group:
            locations.append(min(note.possible_locations))

        unique_locations = list(set(locations))

        unique_locations.sort(reverse=direction)

        return unique_locations

    def max_locations(self, direction: bool) -> list[int]:
        """
        Finds the maximum location for each playable note in either sort direction based
        on direction parameter.

        param direction: The direction to sort the returned list. False ascending and
        true descending

        return: List of integer values of each maximum location sorted based on
        direction state.
        """
        locations: list[int] = []

        for note in self.playable_group:
            locations.append(max(note.possible_locations))

        unique_locations = list(set(locations))

        unique_locations.sort(reverse=direction)

        return unique_locations

    def find_need_points(self) -> None:
        """TODO Might not be fully functioning. Check if need_moves is needed.
        Find each point that the group requires a move when coming from the previous
        group other than the first move.
        """

        in_direction = self.movement_directions[0]

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
        else:
            raise (TypeError("Direction no specified."))

    def find_freed_points(self) -> None:
        """TODO Might not be fully functioning. Check if freed_moves is needed.
        Find each point that the group allows movement towards the next group.
        """
        out_direction = self.movement_directions[1]

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

    def __str__(self) -> str:
        temp = ""
        for playable in self.playable_group:
            temp += str(playable) + "\n"
        return temp

    def __repr__(self) -> str:
        temp = ""
        for playable in self.playable_group:
            temp += repr(playable) + "\n"
        return temp


class PlayableGroupList:
    def __init__(self, note_list: PlayableNoteList) -> None:
        """
        List containing each PlayableGroup for a given PlayableNoteList.

        param note_list: PlayableNoteList that should be grouped by this object.
        """
        self.key_map = note_list.key_map
        """
        A SolenoidIndex object that holds the mapping between midi pitch, key location, and valid 
        hand positions for a giving pitch.
        """
        self.cluster_list: list[PlayableGroupCluster] = []
        self.note_list = note_list
        """The PlayableNoteList that was grouped in this object."""
        self.group_list: list[PlayableGroup] = []
        """A list of PlayableGroups based on the note_list."""
        self.find_groups()

    def find_groups(self) -> None:
        """
        Find the PlayableGroups from the note_list
        """
        temp_group = PlayableGroup()

        for note in self.note_list:
            success = temp_group.append(note)

            if success == OUTSIDE_LOCATION:
                self.group_list.append(temp_group)
                temp_group = PlayableGroup()
                temp_group.append(note)

        self.group_list.append(temp_group)

    def find_directions(self) -> None:
        """
        For each PlayableGroup in this object determine the in and out direction for each group.
        """
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

    def find_clusters(self) -> None:
        """
        Find each PlayableGroupCluster based on the stored group_list.
        """
        temp_cluster = PlayableGroupCluster()
        for group in self.group_list:
            if temp_cluster.add_group(group) == 1:
                self.cluster_list.append(temp_cluster)
                temp_cluster = PlayableGroupCluster()

                if len(self.group_list) > 1:
                    temp_cluster.add_group(group)

    def find_moves(self) -> None:
        """TODO Not used"""

        pass

    def __str__(self) -> str:
        temp = ""
        for playable in self.group_list:
            temp += str(playable) + "\n"
        return temp

    def __repr__(self) -> str:
        temp = ""
        for playable in self.group_list:
            temp += repr(playable) + "\n"
        return temp


class PlayableGroupCluster:
    def __init__(self) -> None:
        """
        Contains a cluster of PlayableGroups that exist within a general direction. This means the first and last group
        will have either no direction for in/out or the same direction for both and every other group will have the same
        in direction and the same out direction as each other. Groups within a cluster should have their optimal
        movement determined within the cluster.
        """
        self.cluster: list[PlayableGroup] = []

    def add_group(self, new_group: PlayableGroup) -> None:
        """
        Attempt to add a group to the current cluster. If the group is an edge group (Same in/out direction) or
        an end group (first or last group) return a TODO otherwise return TODO.

        param new_group: A PlayableGroup that is intended to be added to the group."

        return: An interger value that represents whether the note can be added to the
        current group.
        """
        self.cluster.append(new_group)
        if new_group.movement_directions[1] == 0:
            return 1
        elif new_group.movement_directions[0] == new_group.movement_directions[1]:
            return 1
        else:
            return 0

    def find_absolute_need(
        self,
        current_direction: int,
        current_locations: set[int],
        previous_locations: set[int],
    ) -> int:
        """TODO This isn't right
        Find the absolute need for a given current location set based on a previous location set.

        param current_locations: A set of integers that represent a current groups possible locations.
        param previous_locations: A set of integers that represent a previous groups possible locations.

        return: Returns and integer value as a distance of keys.
        """
        if current_direction == LEFT_DIRECTION:
            distance = min(current_locations) - max(previous_locations)
        elif current_direction == RIGHT_DIRECTION:
            distance = max(current_locations) - min(previous_locations)
        else:
            raise ValueError("All groups by here should have directions assigned.")

        return distance

    def find_absolute_freed(
        self,
        current_direction: int,
        current_locations: set[int],
        previous_locations: set[int],
    ) -> int:
        """
        Find the absolute freed for a previous current location set based on a current location set.

        param current_locations: A set of integers that represent a current groups possible locations.
        param previous_locations: A set of integers that represent a previous groups possible locations.

        return: Returns and integer value as a distance of keys.
        """
        if current_direction == LEFT_DIRECTION:
            distance = min(current_locations) - min(previous_locations)
        elif current_direction == RIGHT_DIRECTION:
            distance = max(current_locations) - max(previous_locations)
        else:
            raise ValueError("All groups by here should have directions assigned.")

        return distance

    def absolutes(self) -> None:
        """
        Finds the absolute need and freed groups for the entire cluster.
        """
        previous_group: PlayableGroup = PlayableGroup()
        groups = self.cluster
        for i in range(0, len(groups)):
            if i != 0:
                current_locations = groups[i].possible_locations
                previous_locations = previous_group.possible_locations
                current_group_direction = groups[i].movement_directions[0]

                need_distance = self.find_absolute_need(
                    current_group_direction, current_locations, previous_locations
                )
                freed_distance = self.find_absolute_freed(
                    current_group_direction, current_locations, previous_locations
                )

                groups[i].set_absolute_need(need_distance)

                previous_group.set_absolute_freed(freed_distance)

            previous_group = group

    def find_edge_moves(self) -> None:
        """
        Finds and sets the first need and last freed points of the clustered groups.
        The first group will only have the freed point set and the last group will only have its
        need point set.
        """
        previous_group: PlayableGroup = PlayableGroup()
        groups = self.cluster

        for i in range(len(groups)):
            if i != 0:
                if groups[i].movement_directions[0] == LEFT_DIRECTION:
                    current_first_note = groups[i].playable_group[0]
                    previous_last_note = previous_group.playable_group[-1]
                    distance = (
                        current_first_note.min_position()
                        - previous_last_note.max_position()
                    )

            previous_group = group

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

    group_list = PlayableGroupList(note_list)

    group_list.find_directions()

    for group in group_list.group_list:
        group.find_need_points()

    for group in group_list.group_list:
        group.find_freed_points()

    group_list.find_clusters()

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
