from constants import Constants
from key import Key

BLACK_ROW = 1
WHITE_ROW = 0


def check_key_count(key_count: int) -> bool:
    if key_count == 88:
        return True
    elif key_count == 76:
        return True
    elif key_count == 61:
        return True
    elif key_count == 49:
        return True
    else:
        return False


class SolenoidPositions:
    def __init__(self, row: int, positions: list[int]) -> None:
        # TODO Check for valid inputs
        self.row = row
        self.positions = positions

    def __str__(self) -> str:
        return str(self.row) + ", " + str(self.positions)


class SolenoidIndex:
    def __init__(self, key_count: int, first_key: Key) -> None:
        # TODO Break into smaller functions
        if not check_key_count(key_count):
            raise ValueError("key_count must be 88, 76, 61, or 49.")

        temp_array = []
        for i in range(0, first_key.midi_number):
            temp_array.append(None)

        note_offset = ord(first_key.step) - ord("A")

        solenoid_positions: list[int] = [0]

        for i in range(first_key.midi_number, first_key.midi_number + key_count):
            if note_offset >= 3 and note_offset < 8:
                if note_offset % 2:
                    new_positions = SolenoidPositions(
                        WHITE_ROW, solenoid_positions.copy()
                    )
                    temp_array.append(new_positions)
                    if first_key.midi_number + key_count - i >= 15:
                        solenoid_positions.insert(0, solenoid_positions[0] + 1)
                        if len(solenoid_positions) > 9:
                            solenoid_positions.pop()
                    else:
                        solenoid_positions.pop()
                        solenoid_positions.insert(0, None)

                else:
                    new_positions = SolenoidPositions(
                        BLACK_ROW, solenoid_positions[1:].copy()
                    )
                    temp_array.append(new_positions)
            else:
                if note_offset % 2:
                    new_positions = SolenoidPositions(
                        BLACK_ROW, solenoid_positions[1:].copy()
                    )
                    temp_array.append(new_positions)
                else:
                    new_positions = SolenoidPositions(
                        WHITE_ROW, solenoid_positions.copy()
                    )
                    temp_array.append(new_positions)
                    if (
                        first_key.midi_number + key_count - i >= 15
                    ):  # TODO Figure out how to determine the cuttoff for pianos other than just 88
                        solenoid_positions.insert(0, solenoid_positions[0] + 1)
                        if len(solenoid_positions) > 9:
                            solenoid_positions.pop()
                    else:
                        solenoid_positions.pop()
                        solenoid_positions.insert(0, None)

            note_offset += 1
            if note_offset == 12:
                note_offset = 0

        temp_array = temp_array + ([None] * (129 - (first_key.midi_number + key_count)))

        self.index_list = tuple(temp_array)

    def __str__(self) -> str:
        return str(self.index_list)


if __name__ == "__main__":
    constants = Constants()

    indexes = SolenoidIndex(88, constants.first_88_key)

    for i, item in enumerate(indexes.index_list):
        print(str(i) + ": " + str(item))
