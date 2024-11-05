from enum import Enum

from playable import PlayableNote


class Hand(Enum):
    RIGHT = 0
    LEFT = 1


class PlayCommand:
    def __init__(
        self, hand: Hand, note: PlayableNote, previous_time: int, time_loss: float
    ) -> None:
        """
        A single deploy of the solenoids of a single hand.

        param hand: A hand enum that represents the hand that will process this command.
        param note: The PlayableNote for this PlayCommand.
        param previous_time: An integer value in absolute musicxml ticks for the previous
        PlayableNote.
        param time_loss: A float value in microseconds that need to be removed from the
        duration for retraction delay and any moves
        """
        pass


class MoveCommand:
    def __init__(
        self, hand: Hand, location: int, note: PlayableNote, previous_time: int
    ) -> None:
        """
        A single move of a single hand.

        param hand: A hand enum that represents the hand that will process this command.
        param note: The PlayableNote that should finish immediately prior to this move.
        param previous_time: An integer value in absolute musicxml ticks for the previous move.
        """
        pass


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
