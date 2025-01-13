import math

from decimal import Decimal
from enum import Enum

from solenoids import SolenoidIndex
from procsss_xml import (
    MusicPiece,
    TempoList,
    DynamicList,
    TaggedNote,
    tick_tag_note,
    extract_pitch,
)
from generated.musicxml import ScorePart, Note, Rest


# TODO change to enum
OUTSIDE_LOCATION = 1
INSIDE_LOCATION = 0

# TODO change to enum


KEYWIDTH = 23.2
actuationTime = 1000
Inital_duration = 5000
maxSpeed = 6000
maxAccel = 60000

US_PER_MINUTE = 1e6 * 60

NOTES_IN_OCTAVE = 12
BASE_OCTAVE_OFFSET = 1


def update_temp_movement(
    temp_movement: int,
    ordered_locations: list[int],
    target_location: int,
    remaining_movement: int,
) -> int:
    """
    TODO
    """
    temp_movement += ordered_locations[0] - target_location

    if abs(temp_movement) > abs(remaining_movement):
        sign_corrected_movement = math.copysign(remaining_movement, temp_movement)
        temp_movement = int(sign_corrected_movement)

    return temp_movement


class Direction(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3


def is_note_chord(note: Note) -> bool:
    """
    TODO

    Things that can make a note "still"
    A chord is still. # Check if this note is a chord and just append to the previous note.
    A set of tied notes are still. # The first note that has a tie (not tied) start should be treated as locking down every note until a tie stop presents.
    A set of notes that overlap, regardless of duration, are still. # Check each notes start tick and compare if it falls inside a previous notes duration. If that happens that the note belongs to the previous StillNotes.

    Chords should be treated and truly single notes. Once in the pcode stage they should be recombined into a single deploy command. Notes with the same start time and duration should be treated as chords
    Ties should be treated as a single pcode command for that specific pitch.
    Ugh
    """
    result = any(isinstance(x, Note.Chord) for x in note.choice)
    return result


def is_note_rest(note: Note) -> bool:
    result = any(isinstance(x, Rest) for x in note.choice)
    return result


def pitch_to_midi(note: Note) -> int:
    """
    Converts a string representation of a pitch to its midi equivilent.

    param letter: The letter of the pitch as a string.
    param octave: The octave of the pitch as an integer.
    param alter: An integer which represents if the note is a sharp or flat.
    """
    (step, octave, alter) = extract_pitch(note)

    note_offset = ord(step) - ord("C")
    octave_offset = (octave + BASE_OCTAVE_OFFSET) * NOTES_IN_OCTAVE

    if note_offset >= 0 and note_offset < 3:
        missing_half_step = 0
    elif note_offset >= 3:
        missing_half_step = 1
    else:
        missing_half_step = -13

    result = ((note_offset * 2) - missing_half_step) + octave_offset + int(alter)

    return result


def convert_tick_time(tempo: Decimal, divisions: Decimal) -> Decimal:
    """
    TODO
    """
    divisions_per_minute = tempo * divisions

    result = Decimal(US_PER_MINUTE) / divisions_per_minute

    return result


def xml_note_time(
    tagged_note: TaggedNote,
    tempo_list: TempoList,
    divisions: Decimal,
) -> Decimal:
    duration_time: Decimal = 0

    note_duration = tick_tag_note(tagged_note.note)

    for i in range(0, int(note_duration)):
        current_tempo = tempo_list.tempo_at_tick(tagged_note.tick + i)
        duration_time += convert_tick_time(current_tempo, divisions)

    return duration_time


def convert_velocity(xml_velocity: Decimal) -> Decimal:
    """
    TODO
    """

    default_forte_midi = 90

    xml_percentage = xml_velocity / 100

    midi_velocity = default_forte_midi * xml_percentage

    return midi_velocity


def xml_dynamic(tagged_note: TaggedNote, dynamic_list: DynamicList) -> int:
    dynamic = dynamic_list.dynamic_at_tick(tagged_note.tick)
    velocity = convert_velocity(dynamic)

    # TODO Account for accents for adjucting velocity

    return int(velocity)


def move_closer_to_zero(lst):
    return [x - 1 if x > 0 else x + 1 if x < 0 else x for x in lst]


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


class UniqueNote:
    def __init__(
        self,
        midi_pitch: int,
        note_start: Decimal,
        duration: Decimal,
        velocity: Decimal,
    ) -> None:
        """TODO"""

        self.midi_pitch = midi_pitch

        self.note_start = note_start

        self.duration = duration

        self.velocity = velocity


class StillNotes:
    def __init__(
        self,
        key_map: SolenoidIndex,
        note_start: Decimal,
        duration: Decimal,
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

        self.unique_notes = [UniqueNote(midi_pitch, note_start, duration, velocity)]

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

        self.next_delay: Decimal = 0
        """An integer value of musicxml ticks until the next note starts. Zero means there is no next note."""

        new_locations = self.key_map.playable_for_pitch(midi_pitch)
        self.possible_locations = set(
            filter(lambda item: item is not None, new_locations)
        )
        """A set that contains every valid location for the hand that allows this note to be played."""

        self.position: int = 0
        """TODO"""

        self.time_loss: float = 0.0

    def add_note(
        self,
        midi_pitch: int,
        note_start: Decimal,
        duration: Decimal,
        velocity: Decimal,
    ) -> int:
        """
        Adds an additional pitch to the note. If the start, duration, and velocity are the same seperate pitches should
        be stored together in the StillNotes using this function. If the pitch cannot be played at the same time
        as each currently stored note then do not add the note and return 1 else return 0.

        param new_midi_pitch: An integer that represents the pitch of the note equivilent to the midi pitch number
                              that will be added to the StillNotes.
        """
        new_locations = self.key_map.playable_for_pitch(midi_pitch)
        filtered_locations = set(filter(lambda item: item is not None, new_locations))
        temp_locations = set(self.possible_locations) & filtered_locations

        if temp_locations:
            self.possible_locations = temp_locations
            self.midi_pitches.append(midi_pitch)
            new_note = UniqueNote(midi_pitch, note_start, duration, velocity)
            self.unique_notes.append(new_note)
            return INSIDE_LOCATION
        else:
            return OUTSIDE_LOCATION

    def max_position(self) -> int:
        """
        Returns the maximum position for this StillNotes.

        return: Integer that represents the maximum possible_location.
        """
        return max(self.possible_locations)

    def min_position(self) -> int:
        """
        Returns the minimum position for this StillNotes.

        return: Integer that represents the minimum possible_location.
        """
        return min(self.possible_locations)

    def set_delay(self, next_start: Decimal) -> None:
        """TODO Might remove"""
        self.next_delay = next_start - self.note_start

    def set_time_loss(self, time_loss: float) -> None:
        """TODO TODO TODO
        Set the time loss for the note in terms of microseconds as a float.

        param time_loss: A float value that represents the total time removed
        from the playing duration for things like moves and solenoid retracts
        """
        self.time_loss = Decimal(time_loss)

    def move_score(
        self,
        distance: int,
        key_width: float,
        acceleration: float,
        velociy: float,
    ) -> float:
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
        score_time = (
            travel_time(distance_mm, acceleration, velociy) + actuationTime
        )  # TODO This needs to not be a file constant. This should be a config value.
        spare_time = self.next_delay - self.duration
        if score_time >= spare_time:
            real_score_time = Decimal(score_time) - spare_time
            note_time = self.duration
            score = real_score_time / note_time
            return score
        else:
            return 0

    def set_position(self, position: int) -> None:
        """
        Add the position to this object in terms of integer keys

        param position: An integer value that represents the position in keys to play this note.
        """
        self.position = position

    def find_time_loss(
        self,
        distance: int,
        key_width: float,
        acceleration: float,
        velociy: float,
    ):
        """
        TODO
        """
        distance_mm = distance * key_width
        lost_time = (
            travel_time(distance_mm, acceleration, velociy) + actuationTime
        )  # TODO This should be a config value not a file constant.
        self.set_time_loss(lost_time)

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


def new_point(locations: list[int], group: list[StillNotes], remaining: int) -> bool:
    another_location = len(locations) > 1
    another_group = len(group)
    another_remaining = remaining > 0

    result = another_location and another_group and another_remaining

    return result


def min_locations(playable_group: list[StillNotes], direction: bool) -> list[int]:
    """
    Finds the minimum location for each playable note in either sort direction based
    on direction parameter.

    param TODO
    param direction: The direction to sort the returned list. False ascending and true descending

    return: List of integer values of each minimum location sorted based on
    direction state.
    """
    locations: list[int] = []

    for note in playable_group:
        locations.append(min(note.possible_locations))

    unique_locations = list(set(locations))

    unique_locations.sort(reverse=direction)

    return unique_locations


def max_locations(playable_group: list[StillNotes], direction: bool) -> list[int]:
    """
    Finds the maximum location for each playable note in either sort direction based
    on direction parameter.

    param direction: The direction to sort the returned list. False ascending and
    true descending

    return: List of integer values of each maximum location sorted based on
    direction state.
    """
    locations: list[int] = []

    for note in playable_group:
        locations.append(max(note.possible_locations))

    unique_locations = list(set(locations))

    unique_locations.sort(reverse=direction)

    return unique_locations


def last_freed_point(
    freed_points: list[list[int]], distance: int, playable_group: list[StillNotes]
) -> None:
    """TODO Does nothing useful atm.
    Add the last freed point based on the first note of the next group.

    param distance: An integer representing distance this group can travel to the next group.
    """
    group_length = len(playable_group)
    if freed_points:
        if freed_points[-1][0] == group_length - 1:
            freed_points[-1][1] += distance
        else:
            freed_points.append([group_length - 1, distance])
    else:
        freed_points.append([group_length - 1, distance])


class StillNotesList:
    def __init__(
        self,
        key_map: SolenoidIndex,
        processed_xml: MusicPiece,
        score_part: ScorePart,
        staff: int,
    ) -> None:
        """
        Takes in a XMLNoteList object and converts it to a list of StillNotess. StillNotess combine same time notes
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
        self.playable_list: list[StillNotes] = []
        """The list of every note in the XMLNoteList in the form of StillNotess."""

        self.moves: list[int] = []
        """Every move that should take place during this StillNotesList as a list of integers."""

        self.divisions = processed_xml.part_divisions(score_part)

        xml_notes = processed_xml.tick_tag_notes(score_part, staff)

        dynamic_list = processed_xml.find_dynamic_list(score_part)
        tempo_list = processed_xml.tempo_list

        self.process_list(xml_notes, tempo_list, dynamic_list)

    def process_list(
        self,
        note_list: list[TaggedNote],
        tempo_list: TempoList,
        dynamic_list: DynamicList,
    ) -> None:
        """
        Processes the note_list into a list of StillNotess.

        param note_list: A XMLNoteList object containing each note for a particular staff of a musicxml part.
        """
        current_us_time = Decimal(0)

        for tagged_note in note_list:
            if is_note_rest(tagged_note.note):
                current_us_time += xml_note_time(
                    tagged_note, tempo_list, self.divisions
                )
            elif self.playable_list:
                previous_playable = self.playable_list[-1]

                midi_pitch = pitch_to_midi(tagged_note.note)

                if is_note_chord(tagged_note.note):
                    velocity = xml_dynamic(tagged_note, dynamic_list)
                    note_duration = xml_note_time(
                        tagged_note, tempo_list, self.divisions
                    )
                    previous_playable.add_note(
                        midi_pitch,
                        current_us_time,
                        note_duration,
                        velocity,
                    )

                else:
                    velocity = xml_dynamic(tagged_note, dynamic_list)
                    note_duration = xml_note_time(
                        tagged_note, tempo_list, self.divisions
                    )

                    temp_playable = StillNotes(
                        self.key_map,
                        current_us_time,
                        note_duration,
                        midi_pitch,
                        velocity,
                    )
                    current_us_time += note_duration
                    self.playable_list[-1].set_delay(temp_playable.note_start)
                    self.playable_list.append(temp_playable)

            else:
                velocity = xml_dynamic(tagged_note, dynamic_list)
                note_duration = xml_note_time(tagged_note, tempo_list, self.divisions)
                midi_pitch = pitch_to_midi(tagged_note.note)

                temp_playable = StillNotes(
                    self.key_map,
                    current_us_time,
                    note_duration,
                    midi_pitch,
                    velocity,
                )
                current_us_time += note_duration
                self.playable_list.append(temp_playable)

    def find_groups(self) -> None:
        self.group_list = PlayableGroupList(self)
        self.group_list.find_directions()

    def find_clusters(self) -> None:
        self.group_list.find_clusters()
        self.group_list.process_clusters()

    def combine_cluster_moves(self) -> None:
        """Combine all the cluster moves into a single list that aligns indexwise to the StillNotesList."""
        for i, cluster in enumerate(self.group_list.cluster_list):
            if i == 0:
                self.moves = cluster.moves
            else:
                overlap = len(cluster.cluster[0].playable_group)
                zip_result = zip(self.moves[-overlap:], cluster.moves[:overlap])
                overlap_moves = [x + y for x, y in zip_result]
                self.moves = (
                    self.moves[:-overlap] + overlap_moves + cluster.moves[overlap:]
                )

    def find_moves(self, key_width: float, acceleration: int, velocity: int) -> None:
        for i, cluster in enumerate(self.group_list.cluster_list):
            cluster.set_cluster_list()
            cluster.find_optimal_moves(key_width, acceleration, velocity)
        self.combine_cluster_moves()

    def find_locations(self) -> None:
        first_group = self.group_list.group_list[0]
        if first_group.movement_directions[1] == Direction.RIGHT:
            current_location = max(first_group.possible_locations)
        else:
            current_location = min(first_group.possible_locations)
        for i, move in enumerate(self.moves):
            self.playable_list[i].set_position(current_location)
            current_location += move

    def find_time_losses(self) -> None:
        for i in range(0, len(self.moves)):
            self.playable_list[i].find_time_loss(
                abs(self.moves[i]), KEYWIDTH, maxAccel, maxSpeed
            )

    def __iter__(self) -> list[StillNotes]:
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

    def __getitem__(self, i: int) -> StillNotes:
        return self.playable_list[i]

    def __setitem__(self, i: int, data: StillNotes) -> None:
        self.playable_list[i] = data


class PlayableGroup:
    def __init__(self) -> None:
        """
        Represents a group of StillNotess that can be played without any hand movement.
        """
        self.playable_group: list[StillNotes] = []
        """A list of Playable notes that can be played without any hand movement."""
        self.possible_locations: set[int] = []
        """Set of values that represent each possible location of hand location for this group."""
        self.movement_directions: list[int] = [Direction.UNKNOWN, Direction.UNKNOWN]
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

    def append(self, note: StillNotes) -> int:
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

    def last_freed_point(self, distance: int) -> None:
        """TODO Does nothing useful atm.
        Add the last freed point based on the first note of the next group.

        param distance: An integer representing distance this group can travel to the next group.
        """
        group_length = len(self.playable_group)
        if self.freed_points:
            if self.freed_points[-1][0] == group_length - 1:
                self.freed_points[-1][1] += distance
            else:
                self.freed_points.append([group_length - 1, distance])
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

    def group_split(
        self, group: list[StillNotes], element: int, direction: int
    ) -> list[list[StillNotes]]:
        if direction == Direction.LEFT:
            if max(group[-1].possible_locations) == element:
                return [group, []]
            for i, item in enumerate(group):
                if max(item.possible_locations) == element:
                    return [group[: i + 1], group[i + 1 :]]
        else:
            if min(group[-1].possible_locations) == element:
                return [group, []]
            for i, item in enumerate(group):
                if min(item.possible_locations) == element:
                    return [group[: i + 1], group[i + 1 :]]

            raise IndexError("Provided element does not exist in group.")

    def find_need_points(self) -> None:
        """
        Find each point that the group requires a move when coming from the previous
        group other than the first move.
        """

        in_direction = self.movement_directions[0]
        remaining_need = abs(self.absolute_need)
        temp_movement = 0
        current_group = self.playable_group.copy()

        if in_direction == Direction.NONE:
            return

        if in_direction == Direction.LEFT:
            ordered_locations = self.min_locations(True)
            while new_point(ordered_locations, current_group, remaining_need):
                target_location = ordered_locations.pop(0)
                temp_movement = update_temp_movement(
                    temp_movement,
                    ordered_locations,
                    target_location,
                    remaining_need,
                )
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

        elif in_direction == Direction.RIGHT:
            ordered_locations = self.max_locations(False)
            while new_point(ordered_locations, current_group, remaining_need):
                target_location = ordered_locations.pop(0)
                temp_movement = update_temp_movement(
                    temp_movement,
                    ordered_locations,
                    target_location,
                    remaining_need,
                )
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
        current_group = list(reversed(self.playable_group))
        group_length = len(current_group)

        if out_direction == Direction.NONE:
            return

        if out_direction == Direction.LEFT:
            ordered_locations = min_locations(self.playable_group, True)
            while new_point(ordered_locations, current_group, remaining_freed):
                target_location = ordered_locations.pop(0)
                temp_movement = update_temp_movement(
                    temp_movement,
                    ordered_locations,
                    target_location,
                    remaining_freed,
                )
                for i, note in enumerate(current_group):
                    min_location = min(note.possible_locations)
                    if min_location == target_location:
                        point_location = group_length - (i + 1)
                        self.freed_points.append([point_location, temp_movement])
                        current_group = current_group[0:i]
                        remaining_freed -= abs(temp_movement)
                        temp_movement = 0
                        break
            self.last_freed_point(-1 * remaining_freed)

        elif out_direction == Direction.RIGHT:
            ordered_locations = max_locations(self.playable_group, False)
            while new_point(ordered_locations, current_group, remaining_freed):
                target_location = ordered_locations.pop(0)
                temp_movement = update_temp_movement(
                    temp_movement,
                    ordered_locations,
                    target_location,
                    remaining_freed,
                )
                for i, note in enumerate(current_group):
                    max_location = max(note.possible_locations)
                    if max_location == target_location:
                        point_location = group_length - (i + 1)
                        self.freed_points.append([point_location, temp_movement])
                        current_group = current_group[0:i]
                        remaining_freed -= abs(temp_movement)
                        temp_movement = 0
                        break
            self.last_freed_point(remaining_freed)

        else:
            raise (TypeError("Direction not specified."))

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
    def __init__(self, note_list: StillNotesList) -> None:
        """
        List containing each PlayableGroup for a given StillNotesList.

        param note_list: StillNotesList that should be grouped by this object.
        """
        self.key_map = note_list.key_map
        """
        A SolenoidIndex object that holds the mapping between midi pitch, key location, and valid 
        hand positions for a giving pitch.
        """
        self.cluster_list: list[PlayableGroupCluster] = []
        """TODO"""
        self.note_list = note_list
        """The StillNotesList that was grouped in this object."""
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
                previous_low_note = min(previous_group.possible_locations)
                current_low_note = min(current_group.possible_locations)

                if previous_low_note < current_low_note:
                    previous_group.set_out_direction(Direction.RIGHT)
                    current_group.set_in_direction(Direction.LEFT)
                else:
                    previous_group.set_out_direction(Direction.LEFT)
                    current_group.set_in_direction(Direction.RIGHT)

            elif i == 0:
                current_group.set_in_direction(Direction.NONE)

            previous_group = groups[i]

        current_group.set_out_direction(Direction.NONE)

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
        self.cluster_playable: list[StillNotes] = []
        """A list all the StillNotess in the cluster"""

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
        if current_direction == Direction.LEFT:
            distance = min(current_locations) - max(previous_locations)
        elif current_direction == Direction.RIGHT:
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
        if current_direction == Direction.LEFT:
            distance = min(current_locations) - min(previous_locations)
        elif current_direction == Direction.RIGHT:
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
                    current_group_direction,
                    previous_width,
                    current_locations,
                    previous_locations,
                )
                freed_distance = self.find_absolute_freed(
                    current_group_direction, current_locations, previous_locations
                )

                groups[i].set_absolute_need(need_distance)
                previous_group.set_absolute_freed(freed_distance)
                # previous_width = len(current_locations)

            previous_group = groups[i]

    def find_cluster_needs(self) -> None:
        """Find all the needed moves for this cluster and store them all in a single list."""

        index_offset: int = 0

        for i, group in enumerate(self.cluster):
            if i != 0:
                self.cluster_need += [
                    [x[0] + index_offset, x[1]] for x in group.need_points
                ]

            index_offset += len(group.playable_group)

    def find_cluster_freeds(self) -> None:
        """Find all the freed moves for this cluster and store then in a single list for each note."""
        index_offset: int = 0
        total_moves: int = 0

        for i, group in enumerate(self.cluster):
            if i != len(self.cluster) - 1:
                freed_list = group.freed_points.copy()
                freed_item = freed_list.pop(0)

                for j in range(0, len(group.playable_group)):
                    if j == freed_item[0]:
                        total_moves += freed_item[1]
                        if len(freed_list) > 0:
                            freed_item = freed_list.pop(0)

                    self.cluster_freed.append(total_moves)

                extra_freed = [self.cluster_freed[-1]] * len(
                    self.cluster[-1].playable_group
                )
                self.cluster_freed += extra_freed

            index_offset += len(group.playable_group)

    def set_cluster_list(self) -> None:
        """Fill the cluster_playable with each separate group list."""
        for group in self.cluster:
            self.cluster_playable += group.playable_group

    def find_optimal_moves(
        self, key_width: float, acceleration: int, velocity: int
    ) -> None:
        """
        Find for the entire cluster the optimal moves for each needed move.
        """
        scores: list[float] = [1.0] * len(self.cluster_playable)
        self.moves = [0] * len(self.cluster_playable)

        for need in self.cluster_need:
            last_note = need[0]
            scores: list[float] = [1.0] * len(self.cluster_playable)
            need_distance = abs(need[1])
            for i in range(1, (need_distance + 1)):
                for j, freed in enumerate(self.cluster_freed):
                    if j < last_note:
                        if abs(freed) >= 1:
                            scores[j] = self.cluster_playable[j].move_score(
                                abs(self.moves[j]) + 1,
                                key_width,
                                acceleration,
                                velocity,
                            )

                    else:
                        break

                if min(scores) >= 1.0:
                    raise ValueError("Minimum score is not <1")
                best_index = min(range(len(scores)), key=scores.__getitem__)
                self.moves[best_index] += int(math.copysign(1, need[1]))
                self.cluster_freed = move_closer_to_zero(self.cluster_freed)
                scores = [1.0] * len(self.cluster_playable)


if __name__ == "__main__":
    import os
    from constants import Constants

    constants = Constants()

    key_map = SolenoidIndex(88, constants.first_88_key)

    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_name = "test.musicxml"

    xml_file = f"{current_directory}/{file_name}"

    processed_xml = MusicPiece(xml_file)

    score_part = processed_xml.parts_list[0]

    note_list = StillNotesList(key_map, processed_xml, score_part, 1)

    note_list.find_groups()
    note_list.find_clusters()
    note_list.find_moves(KEYWIDTH, maxAccel, maxSpeed)
    note_list.find_locations()
    note_list.find_time_losses()

    for i, item in enumerate(note_list.playable_list):
        print(
            f"{i}\nPosition: {item.position} \nNotes: {item.midi_pitches}\nTime Loss: {item.time_loss}\n"
        )


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
