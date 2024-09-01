import kinematics
import numpy
from copy import deepcopy

from decode import CommandList

CLOSED_SOLENOID_CHAR = "\u03a6"
OPEN_SOLENOID_CHAR = "\U0000039f"
KEY_CHAR = "\U0000203e"
DEPRESS_KEY_CHAR = "\U00002534"
DEPRESS_BLANK_KEY = "|"

INITIAL_HAND_POSITION = 0
KEY_WIDTH = 22
KEY_COUNT = 76
SCREEN_OFFSET = 89 - KEY_COUNT
TOP_ROW_OFFSET = 9

MAX_VELOCITY = 300
MAX_ACCELERATION = 3000


BOTTOM_KEY_TO_MIDI = (
    21,
    23,
    24,
    26,
    28,
    29,
    31,
    33,
    35,
    36,
    38,
    40,
    41,
    43,
    45,
    47,
    48,
    50,
    52,
    53,
    55,
    57,
    59,
    60,
    62,
    64,
    65,
    67,
    69,
    71,
    72,
    74,
    76,
    77,
    79,
    81,
    83,
    84,
    86,
    88,
    89,
    91,
    93,
    95,
    96,
    98,
    100,
    101,
    103,
    105,
    107,
    108,
)

MIDDLE_KEY_TO_MIDI = (
    22,
    0,
    25,
    27,
    0,
    30,
    32,
    34,
    0,
    37,
    39,
    0,
    42,
    44,
    46,
    0,
    49,
    51,
    0,
    54,
    56,
    58,
    0,
    61,
    63,
    0,
    66,
    68,
    70,
    0,
    73,
    75,
    0,
    78,
    80,
    82,
    0,
    85,
    87,
    0,
    90,
    92,
    94,
    0,
    97,
    99,
    0,
    102,
    104,
    106,
    0,
)


class PianoFrame:
    def __init__(self) -> None:
        self.white_keys_index = []
        self.black_keys_index = []

        self.white_solenoid_index = []
        self.black_solenoid_index = []

        self.solenoids = [None] * 17

        self.current_position: int = 0

        self.frame_time: float = 0

        self.setup()
        self.default_piano()

    def setup(self):
        missingKey = 2
        for x in range(KEY_COUNT + SCREEN_OFFSET + 1):
            if x % 2:
                self.black_solenoid_index.append(x)
                if missingKey != 2 and missingKey != 6:
                    self.black_keys_index.append(x)
                missingKey += 1
                if missingKey == 7:
                    missingKey = 0
            else:
                self.white_keys_index.append(x)
                self.white_solenoid_index.append(x)

        self.black_keys_index.pop()

    def default_piano(self):
        self.bottomLine = [" "] * (KEY_COUNT + SCREEN_OFFSET)
        self.middleLine = [" "] * (KEY_COUNT + SCREEN_OFFSET)
        self.topLine = [" "] * (KEY_COUNT + SCREEN_OFFSET)

        for x in self.white_keys_index:
            self.bottomLine[x] = KEY_CHAR

        for x in self.black_keys_index:
            self.middleLine[x] = KEY_CHAR

    def populate_hand(self, location: int):
        self.current_position = location

        for x in range(9):
            adjusted_white_solenoid_index = self.white_solenoid_index[x + location]
            self.middleLine[adjusted_white_solenoid_index] = CLOSED_SOLENOID_CHAR
            self.solenoids[x] = adjusted_white_solenoid_index

        for x in range(8):
            adjusted_black_solenoid_index = self.black_solenoid_index[x + location]
            self.topLine[adjusted_black_solenoid_index] = CLOSED_SOLENOID_CHAR
            self.solenoids[x + TOP_ROW_OFFSET] = adjusted_black_solenoid_index

    def clear_hand(self) -> None:
        for sol in self.solenoids:
            if sol % 2:
                self.topLine[sol] = " "
            else:
                self.middleLine[sol] = " "
        self.solenoids = [None] * 17

    def actuate(self, solenoid_locations: list[int], frame_time: float = 0):
        for sol in solenoid_locations:
            if sol < 9:
                self.bottomLine[self.solenoids[sol]] = DEPRESS_KEY_CHAR
                self.middleLine[self.solenoids[sol]] = OPEN_SOLENOID_CHAR
            elif sol < 17:
                if self.solenoids[sol] in self.black_keys_index:
                    self.middleLine[self.solenoids[sol]] = DEPRESS_KEY_CHAR
                else:
                    self.middleLine[self.solenoids[sol]] = DEPRESS_BLANK_KEY
                self.topLine[self.solenoids[sol]] = OPEN_SOLENOID_CHAR
            else:
                raise ValueError("Maximum location value/index is 16.")
        self.frame_time = frame_time

    def shift_hand(self, keys_shift: int, frame_time: float = 0) -> None:
        self.clear_hand()
        self.populate_hand(keys_shift + self.current_position)
        self.frame_time = frame_time

    def retract(self, frame_time: float = 0):
        for i, sol in enumerate(self.solenoids):
            if i < 9:
                self.bottomLine[sol] = KEY_CHAR
                self.middleLine[sol] = CLOSED_SOLENOID_CHAR
            elif i < 17:
                if sol in self.black_keys_index:
                    self.middleLine[sol] = KEY_CHAR
                else:
                    self.middleLine[sol] = " "
                self.topLine[sol] = CLOSED_SOLENOID_CHAR
        self.frame_time = frame_time

    def __str__(self) -> str:
        return (
            "".join(self.topLine)
            + "\n"
            + "".join(self.middleLine)
            + "\n"
            + "".join(self.bottomLine)
        )


class FrameList:
    def __init__(self) -> None:
        self.piano_state: PianoFrame = PianoFrame()
        self.frames: list[PianoFrame] = []

        self.piano_state.populate_hand(INITIAL_HAND_POSITION)

        self.movement: list[float] = []
        self.movement_direction: int = 0

        self.retract_delay: int = 0

    def __capture_frame(self) -> None:
        self.frames.append(deepcopy(self.piano_state))

    def move_hand(self, distance: int):
        self.movement = kinematics.timeDistanceList(
            KEY_WIDTH, MAX_ACCELERATION, MAX_VELOCITY, abs(distance)
        )

        for time in self.movement:
            time += self.piano_state.frame_time

        self.movement_direction = int(numpy.sign(distance))

    def process_command_list(self, command_list: CommandList) -> None:
        while len(command_list.in_order_commands) > 0:
            next_command_time = command_list.in_order_commands[0].duration

            if self.retract_delay > 0 and self.retract_delay < next_command_time:
                self.piano_state.retract(self.retract_delay)
                self.__capture_frame()
                self.retract_delay = 0
                continue

            if len(self.movement) > 0 and self.movement[0] < next_command_time:
                self.piano_state.shift_hand(
                    self.movement_direction, self.movement.pop(0)
                )
                self.__capture_frame()
                continue

            current_command = command_list.in_order_commands.pop(0)

            if current_command.command_type == "d":
                self.piano_state.actuate(
                    current_command.solenoid_locations, next_command_time
                )
                self.retract_delay = (
                    current_command.duration + current_command.longevity
                )
                self.__capture_frame()

            elif current_command.command_type == "h":
                distance_in_keys = (
                    current_command.position / KEY_WIDTH
                ) - self.piano_state.current_position
                self.move_hand(distance_in_keys)

        if self.retract_delay > 0:
            self.piano_state.retract(self.retract_delay)
            self.__capture_frame()
            self.retract_delay = 0

        while len(self.movement) > 0:
            self.piano_state.shift_hand(self.movement_direction, self.movement.pop(0))
            self.__capture_frame()


class AudioFrame:
    def __init__(self) -> None:
        self.midi_notes: list[int] = []

    def line_index_to_midi(self, piano_frame: PianoFrame):
        bottom_indicies = [
            int(i / 2)
            for i, x in enumerate(piano_frame.bottomLine)
            if x == DEPRESS_KEY_CHAR
        ]
        middle_indicies = [
            int((i - 1) / 2)
            for i, x in enumerate(piano_frame.middleLine)
            if x == DEPRESS_KEY_CHAR
        ]

        for i in bottom_indicies:
            self.midi_notes.append(BOTTOM_KEY_TO_MIDI[i + 4])
        for i in middle_indicies:
            self.midi_notes.append(MIDDLE_KEY_TO_MIDI[i + 4])
