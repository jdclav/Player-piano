STEP_LIST = ["A", "B", "C", "D", "E", "F", "G"]


class Key:
    def __init__(self, midi_number: int, octave: int, step: str, alter: int) -> None:
        if midi_number > 128 or midi_number < 0:
            raise ValueError("midi_number must be between 0 and 128.")
        if octave > 8 or octave < 0:
            raise ValueError("octave must be between 0 and 8.")
        if step not in STEP_LIST:
            raise ValueError("step not valid.")
        if alter > 1 or alter < -1:
            raise ValueError("alter must be -1, 1, or 0.")

        self.midi_number: int = midi_number
        self.octave: int = octave
        self.step: str = step
        self.alter: int = alter
