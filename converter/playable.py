from solenoids import SolenoidIndex


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

        self.possible_locations = self.key_map.playable_for_pitch(self.midi_pitches[0])

    def add_pitch(self, new_midi_pitch: int) -> int:
        self.midi_pitches.append(new_midi_pitch)

        new_locations = self.key_map.playable_for_pitch(new_midi_pitch)

        self.possible_locations = set(self.possible_locations).intersection(
            new_locations
        )

        if self.possible_locations:
            return 0
        else:
            return 1


if __name__ == "__main__":
    from constants import Constants

    constants = Constants()

    key_map = SolenoidIndex(88, constants.first_88_key)

    test = PlayableNote(key_map, 0, 10, 42, 80)

    print(test.possible_locations)

    print(test.add_pitch(56))

    print(test.possible_locations)
