from enum import Enum

from solenoids import SolenoidIndex
from playable import PlayableNote, PlayableNoteList
from constants import base_18

# TODO temp constants
RETRACT_TIME = 50000
KEY_WIDTH = 23.2
START_DELAY = 5000


class Hand(Enum):
    RIGHT = 0
    LEFT = 1


class PlayCommand:
    def __init__(
        self,
        hand: Hand,
        note: PlayableNote,
        previous_time: int,
    ) -> None:
        """
        A single deploy of the solenoids of a single hand.

        param hand: A hand enum that represents the hand that will process this command.
        param note: The PlayableNote for this PlayCommand.
        param previous_time: A float value in microseconds from the previous
        PlayCommand.
        param time_loss: A float value in microseconds that need to be removed from the
        duration for retraction delay and any moves
        """
        self.hand = hand
        """The hand the will be using the command."""
        self.note = note
        """The PlayableNote associated with this command."""
        self.previous_time = previous_time
        """A float value in microseconds from the previous PlayCommand."""

        self.hand_parameter: str = ""
        """TODO"""
        self.digit_parameter: str = ""
        """TODO"""
        self.velocity_parameter: str = ""
        """TODO"""
        self.time_parameter: str = ""
        """TODO"""
        self.duration_parameter: str = ""
        """TODO"""

        self.pcode: str = ""
        """TODO"""

    def set_hand_paramter(self) -> None:
        """
        Convert the hand value to the pcode representation.
        """
        self.hand_parameter += "s"
        if self.hand == Hand.RIGHT:
            self.hand_parameter += "0"
        else:
            self.hand_parameter += "1"

    def set_digit_parameter(self, key_map: SolenoidIndex) -> None:
        """
        Convert the pitch(es) from the stored note to the pcode representation for a given key_map and postion.

        param key_map: A SolenoidIndex object that relates pitch, position, and solenoid.
        param position: An integer value for the position in terms of piano keys.
        """
        self.digit_parameter += "n"
        for i, pitch in enumerate(self.note.midi_pitches):
            index_list = key_map.index_list[pitch]
            locations_list = index_list.positions
            solenoid_position = locations_list.index(self.note.position) + (
                index_list.row * 9
            )
            # TODO How to assign "finger" to solenoid
            base = base_18()
            self.digit_parameter += str(base[solenoid_position])

        for _ in range(i, 4):
            self.digit_parameter += str(base[-1])

    def set_velocity_paramter(self) -> None:
        """TODO"""
        self.velocity_parameter += "f"
        self.velocity_parameter += "10"  # TODO current velocity is not tracked correctly str(self.note.velocity)

    def set_time_parameter(self, us_per_tick: float) -> None:
        """TODO"""
        self.time_parameter += "t"
        relative_start = self.note.note_start - self.previous_time
        relative_start_us = relative_start * us_per_tick
        # TODO adapt from ms to us in the future
        relative_start_ms = int(relative_start_us / 1000)
        self.time_parameter += str(relative_start_ms)

    def set_duration_parameter(self, us_per_tick: float) -> None:
        """TODO"""
        self.duration_parameter += "l"
        ideal_duration_us = self.note.duration * us_per_tick
        actual_duration_us = ideal_duration_us - self.note.time_loss
        # TODO adapt from ms to ms in the future
        actual_duration_ms = int(actual_duration_us / 1000)
        self.duration_parameter += str(actual_duration_ms)

    def generate_pcode(self, us_per_tick: float, key_map: SolenoidIndex) -> None:
        """TODO"""
        self.set_hand_paramter()
        self.set_digit_parameter(key_map)
        self.set_velocity_paramter()
        self.set_time_parameter(us_per_tick)
        self.set_duration_parameter(us_per_tick)
        self.pcode += "d"
        self.pcode += " "
        self.pcode += self.hand_parameter
        self.pcode += " "
        self.pcode += self.digit_parameter
        self.pcode += " "
        self.pcode += self.velocity_parameter
        self.pcode += " "
        self.pcode += self.time_parameter
        self.pcode += " "
        self.pcode += self.duration_parameter

    def set_first_time(self, initial_time: int) -> None:
        """TODO"""
        self.pcode = ""
        self.pcode += "d"
        self.pcode += " "
        self.pcode += self.hand_parameter
        self.pcode += " "
        self.pcode += self.digit_parameter
        self.pcode += " "
        self.pcode += self.velocity_parameter
        self.pcode += " "
        self.pcode += f"t{initial_time}"
        self.pcode += " "
        self.pcode += self.duration_parameter


class MoveCommand:
    def __init__(
        self,
        hand: Hand,
        note: PlayableNote,
        next_note: PlayableNote,
        previous_move_time: float,
    ) -> None:
        """
        A single move of a single hand.

        param hand: A hand enum that represents the hand that will process this command.
        param note: The PlayableNote that should finish immediately prior to this move.
        param previous_time: An integer value in absolute musicxml ticks for the previous move.
        """
        self.hand = hand
        """TODO"""
        self.note = note
        """TODO"""
        self.next_note = next_note
        """TODO"""
        self.previous_move_time = previous_move_time
        """TODO"""

        self.hand_parameter: str = ""
        """TODO"""
        self.position_parameter: str = ""
        """TODO"""
        self.time_parameter: str = ""
        """TODO"""
        self.duration_parameter: str = ""
        """TODO"""

        self.pcode: str = ""
        """TODO"""

    def set_hand_paramter(self) -> None:
        """
        Convert the hand value to the pcode representation.
        """
        self.hand_parameter += "s"
        if self.hand == Hand.RIGHT:
            self.hand_parameter += "0"
        else:
            self.hand_parameter += "1"

    def set_position_parameter(self, key_width: float) -> None:
        """TODO"""
        self.position_parameter += "p"
        self.position_parameter += str(int(key_width * self.next_note.position))

    def set_time_parameter(
        self,
        us_per_tick: float,
        retract_time: float,
    ) -> None:
        """TODO"""
        self.time_parameter += "t"
        abs_start_us = (
            ((self.note.note_start + self.note.duration) * us_per_tick)
            + retract_time
            - self.note.time_loss
        )
        relative_start_us = abs_start_us - self.previous_move_time
        # TODO adapt from ms to us in the future
        relative_start_ms = int(relative_start_us / 1000)
        self.time_parameter += str(relative_start_ms)

    def set_duration_parameter(
        self,
        us_per_tick: float,
        retract_time: float,
    ) -> None:
        """TODO"""
        self.duration_parameter += "l"
        note_diff_ticks = self.note.next_delay
        duration_ticks = note_diff_ticks - self.note.duration
        ideal_duration_us = duration_ticks * us_per_tick
        move_duration_us = (ideal_duration_us - retract_time) + self.note.time_loss
        # TODO adapt from ms to ms in the future
        move_duration_ms = int(move_duration_us / 1000)
        self.duration_parameter += str(move_duration_ms)

    def set_first_times(self):
        """TODO"""
        self.time_parameter += "t0"
        self.duration_parameter += "l" + str(START_DELAY)

    def generate_pcode(
        self,
        us_per_tick: float,
        key_width: float,
        retract_time: float,
    ) -> None:
        """TODO"""
        self.set_hand_paramter()
        self.set_position_parameter(key_width)

        if self.note.position == self.note.position:
            self.set_first_times()
        else:
            self.set_time_parameter(us_per_tick, retract_time)
            self.set_duration_parameter(us_per_tick, retract_time)

        self.pcode += "h"
        self.pcode += " "
        self.pcode += self.hand_parameter
        self.pcode += " "
        self.pcode += self.position_parameter
        self.pcode += " "
        self.pcode += self.time_parameter
        self.pcode += " "
        self.pcode += self.duration_parameter


class PlayList:
    def __init__(
        self, note_list: PlayableNoteList, key_map: SolenoidIndex, us_per_tick: float
    ) -> None:
        """TODO
        An entire list of PlayCommands for a single hand.
        """

        self.note_list = note_list
        """TODO"""
        self.key_map = key_map
        """TODO"""
        self.us_per_tick = us_per_tick
        """TODO"""

        self.play_commands: list[PlayCommand] = []
        """TODO"""

    def generate_play_list(self, hand: Hand) -> None:
        previous_time: float = 0
        for note in self.note_list.playable_list:
            play_command = PlayCommand(hand, note, previous_time)
            play_command.generate_pcode(self.us_per_tick, self.key_map)
            self.play_commands.append(play_command)
            previous_time = note.note_start

        self.play_commands[0].set_first_time(START_DELAY)

    def __str__(self):
        temp_string = ""
        for item in self.play_commands:
            temp_string = temp_string + item.pcode + "\n"

        return temp_string


class MoveList:
    def __init__(
        self, note_list: PlayableNoteList, key_map: SolenoidIndex, us_per_tick: float
    ) -> None:
        """TODO
        An entire list of MoveCommands for a single hand.
        """

        self.note_list = note_list
        """TODO"""
        self.key_map = key_map
        """TODO"""
        self.us_per_tick = us_per_tick
        """TODO"""

        self.move_commands: list[MoveCommand] = []
        """TODO"""

    def generate_move_list(
        self, hand: Hand, key_width: float, retract_time: float
    ) -> None:
        """TODO"""
        previous_time: float = 0

        for i in range(0, len(self.note_list.playable_list)):
            if i == 0:
                move_command = MoveCommand(
                    hand, self.note_list[i], self.note_list[i], previous_time
                )
                move_command.generate_pcode(self.us_per_tick, key_width, retract_time)

                self.move_commands.append(move_command)

            else:
                if self.note_list[i].position != self.note_list[i - 1].position:
                    move_command = MoveCommand(
                        hand, self.note_list[i - 1], self.note_list[i], previous_time
                    )
                    move_command.generate_pcode(
                        self.us_per_tick, key_width, retract_time
                    )

                    self.move_commands.append(move_command)

    def __str__(self):
        temp_string = ""
        for item in self.move_commands:
            temp_string = temp_string + item.pcode + "\n"

        return temp_string


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

    first_part = music_xml.part_ids[0]

    first_staff = music_xml.generate_note_list(first_part)[0]

    music_xml.us_per_division(first_part.id)

    note_list = PlayableNoteList(key_map, first_staff)

    note_list.find_groups()
    note_list.find_clusters()
    note_list.set_tick_duration(music_xml.us_per_div)
    note_list.find_moves(23.2, constants.max_acceleration, constants.max_velocity)
    note_list.find_locations()
    note_list.find_time_losses()

    play_commands = PlayList(note_list, key_map, music_xml.us_per_div)
    play_commands.generate_play_list(Hand.RIGHT)

    move_commands = MoveList(note_list, key_map, music_xml.us_per_div)
    move_commands.generate_move_list(Hand.RIGHT, 23.2, 50000)

    print(str(play_commands) + str(move_commands))
