import math

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

keyWidth = 23.2
actuationTime = 50000
Inital_duration = 5000
maxSpeed = 300
maxAccel = 3000

def travel_time(distance, accel, velocity):
    """TODO Verify and update"""
    mAccelDistance = (velocity**2) / (2 * accel)
    if mAccelDistance > distance:
        rDistance = 0
        accelDistance = distance
    else:
        accelDistance = mAccelDistance
        rDistance = distance - accelDistance

    accelTime = 2 * math.sqrt(accelDistance / (accel))
    linearTime = rDistance / velocity
    totalTime = accelTime + linearTime
    return totalTime * 1000000

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

        self.next_delay: int = 0
        """An integer value of musicxml ticks until the next note starts. Zero means there is no next note."""

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
    
    def set_delay(self, next_start: int) -> None:
        self.next_delay = next_start - self.note_start
    
    def move_score(self, distance: int, us_per_tick: float, key_width: float, acceleration: float, velociy: float) -> float:
        """
        Takes in a distance to be traveled after the note is played and returns a score based on how much it affects 
        the note. A lower score means the note was affected less. A score of over 1 means the entered distance cannot 
        be traveled after playing this note.

        param distance: An integer value for the number of keys that need to be moved.
        param key_width: A float value that represents the width of a piano key in mm.
        
        return: A float value that represents the score of this potential move. A lower score is better and a score of 
        over 1 means the entered distance cannot be traveled after playing this note.
        """
        distance_mm = distance * key_width
        score_time = travel_time(distance_mm, acceleration, velociy) + actuationTime
        spare_time = (self.next_delay - self.duration) * us_per_tick
        if(score_time >= spare_time):
            real_score_time = score_time - spare_time
            note_time = self.duration * us_per_tick
            score = real_score_time / note_time
            return score
        else:
            return 0

    
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

        self.us_per_tick = 0

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
                    self.playable_list[-1].set_delay(temp_playable.note_start)
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

    def set_tick_duration(self, us_per_tick: float) -> None:
        self.us_per_tick = us_per_tick

    def find_groups(self) -> None:
        self.group_list = PlayableGroupList(self)
        self.group_list.find_directions()

    def find_clusters(self) -> None:
        self.group_list.find_clusters()
        self.group_list.process_clusters()

    def find_moves(self, key_width: float, acceleration: int, velocity: int) -> None:
        for cluster in self.group_list.cluster_list:
            cluster.set_cluster_list()
            cluster.find_optimal_moves(self.us_per_tick, key_width, acceleration, velocity)

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
        self.freed_points: list[list[int, int]] = []
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

    def first_need_point(self, distance: int) -> None:
        """
        Add the first need point based on the last note of the previous group.

        param distance: An integer representing distance needed to travel to this group from the last group.
        """
        self.need_points.insert(0, [0, distance])


        group_length = len(self.playable_group)
        if(self.need_points[-1][0] == group_length - 1):
            self.need_points[-1][1] += distance
        else:
            self.need_points.append([group_length - 1, distance])

    def last_freed_point(self, distance: int) -> None:
        """TODO Does nothing useful atm.
        Add the last freed point based on the first note of the next group.

        param distance: An integer representing distance this group can travel to the next group. 
        """
        group_length = len(self.playable_group)
        if(self.freed_points[-1][0] == group_length - 1):
            self.freed_points[-1][1] += distance
        else:
            self.freed_points.append([group_length - 1, distance])

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
    
    def group_split(self, group: list[PlayableNote], element: int, direction: int) -> list[list[PlayableNote]]:
        if direction == LEFT_DIRECTION:
            if max(group[-1].possible_locations) == element:
                return [group, []]
            for i, item in enumerate(group):
                if max(item.possible_locations) == element:
                    return [group[:i + 1], group[i + 1:]]
        else:
            if min(group[-1].possible_locations) == element:
                return [group, []]
            for i, item in enumerate(group):
                if min(item.possible_locations) == element:
                    return [group[:i + 1], group[i + 1:]]
                
            raise IndexError("Provided element does not exist in group.")

    def find_need_points(self) -> None:
        """
        Find each point that the group requires a move when coming from the previous
        group other than the first move.
        """

        in_direction = self.movement_directions[0]
        remaining_need = abs(self.absolute_need)
        temp_movement = 0

        if in_direction == NO_DIRECTION:
            return

        if in_direction == LEFT_DIRECTION:
            ordered_locations = self.min_locations(True)
            current_group = self.playable_group.copy()
            while len(ordered_locations) > 1 and len(current_group) > 1 and remaining_need > 0:
                target_location = ordered_locations.pop(0)
                temp_movement += target_location - ordered_locations[0]
                for i, note in enumerate(current_group):
                    min_location = min(note.possible_locations)
                    if min_location == target_location:
                        self.need_points.append([i, temp_movement])
                        current_group = current_group[0:i]
                        remaining_need -= abs(temp_movement)
                        temp_movement = 0
                        break
            self.need_points.reverse()
            self.first_need_point(remaining_need)
                

        elif in_direction == RIGHT_DIRECTION:
            ordered_locations = self.max_locations(False)
            current_group = self.playable_group.copy()
            while len(ordered_locations) > 1 and len(current_group) > 1 and remaining_need > 0:
                target_location = ordered_locations.pop(0)
                temp_movement += target_location - ordered_locations[0]
                for i, note in enumerate(current_group):
                    max_location = max(note.possible_locations)
                    if max_location == target_location:
                        self.need_points.append([i, temp_movement])
                        current_group = current_group[0:i]
                        remaining_need -= abs(temp_movement)
                        temp_movement = 0
                        break
            self.need_points.reverse()
            self.first_need_point(-1 * remaining_need)
        else:
            raise (TypeError("Direction no specified."))
        
        

    def find_freed_points(self) -> None:
        """
        Find each point that the group allows movement towards the next group..
        """
        out_direction = self.movement_directions[1]
        remaining_freed = abs(self.absolute_freed)
        temp_movement = 0

        if out_direction == NO_DIRECTION:
            return

        if out_direction == LEFT_DIRECTION:
            ordered_locations = self.min_locations(True)
            current_group = list(reversed(self.playable_group))
            group_length = len(current_group)
            while len(ordered_locations) > 1 and len(current_group) > 1 and remaining_freed > 0:
                target_location = ordered_locations.pop(0)
                temp_movement += ordered_locations[0] - target_location
                for i, note in enumerate(current_group):
                    min_location = min(note.possible_locations)
                    if min_location == target_location:
                        self.freed_points.append([group_length - (i + 1), temp_movement])
                        current_group = current_group[0:i]
                        remaining_freed -= abs(temp_movement)
                        temp_movement = 0
                        break
            self.last_freed_point(-1 * remaining_freed)

        elif out_direction == RIGHT_DIRECTION:
            ordered_locations = self.max_locations(False)
            current_group = list(reversed(self.playable_group))
            group_length = len(current_group)
            while len(ordered_locations) > 1 and len(current_group) > 1 and remaining_freed > 0:
                target_location = ordered_locations.pop(0)
                temp_movement += ordered_locations[0] - target_location
                for i, note in enumerate(current_group):
                    max_location = max(note.possible_locations)
                    if max_location == target_location:
                        self.freed_points.append([group_length - (i + 1), temp_movement])
                        current_group = current_group[0:i]
                        remaining_freed -= abs(temp_movement)
                        temp_movement = 0
                        break
            self.last_freed_point(remaining_freed)
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
        """TODO"""
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

    def process_clusters(self) -> None:
        """
        Once Clusters have been found they should be processed to determine values needed by the clusters to 
        find the optimal moves.
        """
        for cluster in self.cluster_list:
            cluster.absolutes()
        for group in self.group_list:
            group.find_need_points()
        for group in self.group_list:
            group.find_freed_points()
        for cluster in self.cluster_list:
            cluster.find_cluster_needs()
        for cluster in self.cluster_list:
            cluster.find_cluster_freeds()

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
        """A list of PlayableGroups that all share a general direction."""
        self.cluster_need: list[list[int, int]] = []
        """
        A list of integer pairs that contain the needs of each group in the cluster. Indexes are adjusted
        so that group 0 note 0 is index 0 for all groups.
        """
        self.cluster_freed: list[list[int, int]] = []
        """
        A list of integers that represent the freed movement at a given index of each group in the cluster. 
        Indexes are adjusted so that group 0 note 0 is index 0 for all groups.
        """
        self.moves: list[int] = []
        """A list of locations a move will take place and how much it will move."""
        self.cluster_playable: list[PlayableNote] = []
        """A list all the PlayableNotes in the cluster"""

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
        previous_width: int,
        current_locations: set[int],
        previous_locations: set[int],
    ) -> int:
        """
        Find the absolute need for a given current location set based on a previous location set.

        param current_direction: An integer that represents the in direction the current group.
        param previous_width: An integer that represents the previous groups possible location width.
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

        return distance + previous_width

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
        Finds the absolute need and freed distances for the entire cluster.
        """
        previous_group: PlayableGroup = PlayableGroup()
        groups = self.cluster
        previous_width = 0
        
        for i in range(0, len(groups)):

            if i != 0:
                current_locations = groups[i].possible_locations
                previous_locations = previous_group.possible_locations
                current_group_direction = groups[i].movement_directions[0]

                need_distance = self.find_absolute_need(
                    current_group_direction, previous_width, current_locations, previous_locations
                )
                freed_distance = self.find_absolute_freed(
                    current_group_direction, current_locations, previous_locations
                )

                groups[i].set_absolute_need(need_distance)
                previous_group.set_absolute_freed(freed_distance)
                previous_width = len(current_locations)

            previous_group = groups[i]

    def find_cluster_needs(self) -> None:
        """Find all the needed moves for this cluster and store them all in a single list."""

        index_offset: int = 0

        for i, group in enumerate(self.cluster):

            if i != 0:
                self.cluster_need += [[x[0]+index_offset, x[1]] for x in group.need_points]

            index_offset += len(group.playable_group)

    def find_cluster_freeds(self) -> None:
        """Find all the needed moves for this cluster and store then in a single list for each note."""
        index_offset: int = 0
        total_moves: int = 0

        for i, group in enumerate(self.cluster):

            if i != len(self.cluster) - 1:
                freed_list = group.freed_points.copy()
                freed_item = freed_list.pop(0)

                for j in range(0, len(group.playable_group)):
                    if(j == freed_item[0]):
                        total_moves += freed_item[1]
                        if(len(freed_list) > 0):
                            freed_item = freed_list.pop(0)

                    self.cluster_freed.append(total_moves)  
                
                extra_freed = [self.cluster_freed[-1]] * len(self.cluster[-1].playable_group)
                self.cluster_freed += extra_freed

            index_offset += len(group.playable_group)
    def set_cluster_list(self) -> None:
        """Fill the cluster_playable with each separate group list."""
        for group in self.cluster:
            self.cluster_playable += group.playable_group

    def find_optimal_moves(self, us_per_tick: float, key_width: float, acceleration: int, velocity: int) -> None:
        """
        Find for the entire cluster the optimal moves for each needed move.
        """
        scores: list[float] = [1.0] * len(self.cluster_playable)
        self.moves = [0] * len(self.cluster_playable)

        for need in self.cluster_need:
            last_note = need[0]
            need_distance = abs(need[1])
            for i in range(1, (need_distance + 1)):
                for j, freed in enumerate(self.cluster_freed):
                    if(j < last_note):
                        if(abs(freed) >= need_distance):
                            scores[j] = self.cluster_playable[j].move_score(abs(self.moves[j]) + 1, 
                                                                            us_per_tick, 
                                                                            key_width, 
                                                                            acceleration, 
                                                                            velocity)
                    else:
                        break
                    
                if(min(scores) > 1):
                    raise ValueError("Minimum score is not <1")
                best_index = min(range(len(scores)), key=scores.__getitem__)

                self.moves[best_index] += need[1]

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

    music_xml.us_per_division(first_part.id)

    note_list = PlayableNoteList(key_map, first_staff)

    note_list.find_groups()
    note_list.find_clusters()
    note_list.set_tick_duration(music_xml.us_per_div)
    note_list.find_moves(keyWidth, constants.max_acceleration, constants.max_velocity)

    print(note_list)


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
