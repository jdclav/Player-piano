from enum import Enum

from solenoids import SolenoidIndex
from playable import StillNotes, StillNotesList
from constants import base_18

"""
TODO TODO TODO

general changes to pcode.

Various parameters for the pcode file should show up after the s. These should be parameters that need to be adhered to for the pcode to operate correctly
ex. retract time, key width, key count, velocity, acceleration, etc

Time should be changed from relative us between each command to an absolute time. The time should be a uint64 since that can hold over 500,000 years worth of time.

"""

# TODO temp constants
RETRACT_TIME = 50000
KEY_WIDTH = 23.2
START_DELAY = 5000
KEYWIDTH = 23.2


class Hand(Enum):
    RIGHT = 0
    LEFT = 1


class PlayCommand:
    def __init__(
        self,
        hand: Hand,
        note: StillNotes,
        previous_time: float,
    ) -> None:
        """
        A single deploy of the solenoids of a single hand.

        param hand: A hand enum that represents the hand that will process this command.
        param note: The StillNotes for this PlayCommand.
        param previous_time: The previous note from this PlayCommand.
        """
        self.hand = hand
        """The hand the will be using the command."""
        self.note = note
        """The StillNotes associated with this command."""
        self.previous_time = previous_time
        # """A float value in microseconds from the previous PlayCommand."""

        self.hand_parameter: int = 0
        """TODO"""
        self.digit_parameter: str = ""
        """TODO"""
        self.velocity_parameter: int = 0
        """TODO"""
        self.time_parameter: int = 0
        """TODO"""
        self.duration_parameter: int = 0
        """TODO"""

        self.pcode: str = ""
        """TODO"""

    def set_hand_paramter(self) -> None:
        """
        Convert the hand value to the pcode representation.
        """
        self.hand_parameter = self.hand.value

    def set_digit_parameter(self, key_map: SolenoidIndex) -> None:
        """
        Convert the pitch(es) from the stored note to the pcode representation for a given key_map and postion.

        param key_map: A SolenoidIndex object that relates pitch, position, and solenoid.
        param position: An integer value for the position in terms of piano keys.
        """
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
        self.velocity_parameter = self.note.velocity

    def set_time_parameter(self) -> None:
        """TODO"""
        relative_start_us = self.note.note_start - self.previous_time
        # TODO adapt from ms to us in the future
        relative_start_ms = int(relative_start_us / 1000)
        self.time_parameter = relative_start_ms

    def set_duration_parameter(self) -> None:
        """TODO"""
        ideal_duration_us = self.note.duration
        actual_duration_us = ideal_duration_us - self.note.time_loss
        # TODO adapt from ms to ms in the future
        actual_duration_ms = int(actual_duration_us / 1000)
        self.duration_parameter = actual_duration_ms

    def generate_pcode(self, key_map: SolenoidIndex) -> None:
        """TODO"""
        self.set_hand_paramter()
        self.set_digit_parameter(key_map)
        self.set_velocity_paramter()
        self.set_time_parameter()
        self.set_duration_parameter()
        self.pcode += "d"
        self.pcode += " s"
        self.pcode += str(self.hand_parameter)
        self.pcode += " n"
        self.pcode += self.digit_parameter
        self.pcode += " f"
        self.pcode += str(self.velocity_parameter)
        self.pcode += " t"
        self.pcode += str(self.time_parameter)
        self.pcode += " l"
        self.pcode += str(self.duration_parameter)

    def set_first_time(self, initial_time: int) -> None:
        """TODO"""
        self.pcode = ""
        self.pcode += "d"
        self.pcode += " s"
        self.pcode += str(self.hand_parameter)
        self.pcode += " n"
        self.pcode += self.digit_parameter
        self.pcode += " f"
        self.pcode += str(self.velocity_parameter)
        self.pcode += " t"
        self.pcode += str(initial_time)
        self.pcode += " l"
        self.pcode += str(self.duration_parameter)


class MoveCommand:
    def __init__(
        self,
        hand: Hand,
        note: StillNotes,
        next_note: StillNotes,
        previous_move_time: float,
    ) -> None:
        """
        A single move of a single hand.

        param hand: A hand enum that represents the hand that will process this command.
        param note: The StillNotes that should finish immediately prior to this move.
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

        self.hand_parameter: int = 0
        """TODO"""
        self.position_parameter: int = 0
        """TODO"""
        self.time_parameter: int = 0
        """TODO"""
        self.duration_parameter: int = 0
        """TODO"""

        self.pcode: str = ""
        """TODO"""

    def set_hand_paramter(self) -> None:
        """
        Convert the hand value to the pcode representation.
        """
        self.hand_parameter = self.hand.value

    def set_position_parameter(self, key_width: float) -> None:
        """TODO"""
        self.position_parameter = int(key_width * self.next_note.position)

    def set_time_parameter(
        self,
        retract_time: float,
    ) -> None:
        """TODO"""

        abs_start_us = (
            (self.note.note_start + self.note.duration)
            + retract_time
            - self.note.time_loss
        )

        relative_start_us = abs_start_us - self.previous_move_time
        # TODO adapt from ms to us in the future
        relative_start_ms = int(relative_start_us / 1000)
        self.time_parameter = relative_start_ms

    def set_duration_parameter(
        self,
        retract_time: float,
    ) -> None:
        """TODO"""
        note_diff_time = self.note.next_delay
        duration_ticks = note_diff_time - self.note.duration
        ideal_duration_us = duration_ticks
        move_duration_us = (ideal_duration_us - retract_time) + self.note.time_loss
        # TODO adapt from ms to ms in the future
        move_duration_ms = int(move_duration_us / 1000)
        self.duration_parameter = move_duration_ms

    def set_first_times(self):
        """TODO"""
        self.time_parameter = 0
        self.duration_parameter = START_DELAY

    def generate_pcode(
        self,
        key_width: float,
        retract_time: float,
    ) -> None:
        """TODO"""
        self.set_hand_paramter()
        self.set_position_parameter(key_width)

        if self.note.note_start == self.next_note.note_start:
            self.set_first_times()
        else:
            self.set_time_parameter(retract_time)
            self.set_duration_parameter(retract_time)

        self.pcode += "h"
        self.pcode += " s"
        self.pcode += str(self.hand_parameter)
        self.pcode += " p"
        self.pcode += str(self.position_parameter)
        self.pcode += " d"
        self.pcode += str(self.time_parameter)
        self.pcode += " l"
        self.pcode += str(self.duration_parameter)


class PlayList:
    def __init__(self, note_list: StillNotesList, key_map: SolenoidIndex) -> None:
        """TODO
        An entire list of PlayCommands for a single hand.
        """

        self.note_list = note_list
        """TODO"""
        self.key_map = key_map
        """TODO"""

        self.play_commands: list[PlayCommand] = []
        """TODO"""

    def generate_play_list(self, hand: Hand) -> None:
        previous_time: float = 0
        for note in self.note_list.playable_list:
            play_command = PlayCommand(hand, note, previous_time)
            play_command.generate_pcode(self.key_map)
            self.play_commands.append(play_command)
            previous_time = note.note_start

        self.play_commands[0].set_first_time(START_DELAY)

    def __str__(self):
        temp_string = ""
        for item in self.play_commands:
            temp_string = temp_string + item.pcode + "\n"

        return temp_string


class MoveList:
    def __init__(self, note_list: StillNotesList, key_map: SolenoidIndex) -> None:
        """TODO
        An entire list of MoveCommands for a single hand.
        """

        self.note_list = note_list
        """TODO"""
        self.key_map = key_map
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
                move_command.generate_pcode(key_width, retract_time)

                self.move_commands.append(move_command)

                previous_time = -1 * START_DELAY * 1000

            else:
                if self.note_list[i].position != self.note_list[i - 1].position:
                    move_command = MoveCommand(
                        hand, self.note_list[i - 1], self.note_list[i], previous_time
                    )
                    move_command.generate_pcode(key_width, retract_time)

                    self.move_commands.append(move_command)

                    previous_time += move_command.time_parameter * 1000

    def __str__(self):
        temp_string = ""
        for item in self.move_commands:
            temp_string = temp_string + item.pcode + "\n"

        return temp_string


if __name__ == "__main__":
    import os
    from constants import Constants
    from procsss_xml import MusicPiece

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
    note_list.find_moves(KEYWIDTH, constants.max_acceleration, constants.max_velocity)
    note_list.find_locations()
    note_list.find_time_losses()

    play_commands = PlayList(note_list, key_map)
    play_commands.generate_play_list(Hand.RIGHT)

    move_commands = MoveList(note_list, key_map)
    move_commands.generate_move_list(Hand.RIGHT, 23.2, 50000)

    print(str(play_commands) + str(move_commands))
