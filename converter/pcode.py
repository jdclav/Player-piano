from enum import Enum

from solenoids import SolenoidIndex
from playable import PlayableNote
from constants import base_18


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
            self.digit_parameter += str(base[solenoid_position + 1])

        for _ in range(i, 4):
            self.digit_parameter += "0"

    def set_velocity_paramter(self) -> None:
        """TODO"""
        self.velocity_parameter += "f"
        self.velocity_parameter += str(self.note.velocity)

    def set_time_parameter(self, us_per_tick: float) -> None:
        """TODO"""
        self.time_parameter += "t"
        relative_start = self.note.note_start - self.previous_time
        relative_start_us = relative_start * us_per_tick
        # TODO adapt from ms to ms in the future
        relative_start_ms = int(relative_start_us / 1000)
        self.time_parameter += str(relative_start_ms)

    def set_duration_parameter(self, us_per_tick: float) -> None:
        """TODO"""
        self.duration_parameter += "l"
        ideal_duration_us = note.duration * us_per_tick
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
        pass


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
        # TODO adapt from ms to ms in the future
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
        move_duration_us = (ideal_duration_us - retract_time) + note.time_loss
        # TODO adapt from ms to ms in the future
        move_duration_ms = int(move_duration_us / 1000)
        self.duration_parameter += str(move_duration_ms)

    def generate_pcode(
        self,
        us_per_tick: float,
        key_width: float,
        retract_time: float,
    ) -> None:
        """TODO"""
        self.set_hand_paramter()
        self.set_position_parameter(key_width)
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
    def __init__(self) -> None:
        """
        An entire list of PlayCommands for a single hand.
        """
        pass


class MoveList:
    def __init__(self) -> None:
        """
        An entire list of MoveCommands for a single hand.
        """
        pass


if __name__ == "__main__":
    from constants import Constants

    constants = Constants()

    key_map = SolenoidIndex(88, constants.first_88_key)

    note = PlayableNote(key_map, 10000, 20000, 40, 20)
    note.add_pitch(45)
    note.set_position(8)
    note.set_time_loss(10000)

    note_after = PlayableNote(key_map, 40000, 20000, 48, 20)
    note_after.add_pitch(51)
    note_after.set_position(10)
    note_after.set_time_loss(0)

    note.set_delay(40000)

    play_command = PlayCommand(Hand.RIGHT, note, 0)
    play_command.generate_pcode(10, key_map)

    play_after_command = PlayCommand(Hand.RIGHT, note_after, note.note_start)
    play_after_command.generate_pcode(10, key_map)

    move_command = MoveCommand(Hand.RIGHT, note, note_after, 0)
    move_command.generate_pcode(10, 23.2, 20000)

    print(play_command.pcode)
    print(play_after_command.pcode)

    print(move_command.pcode)
