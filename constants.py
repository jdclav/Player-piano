import yaml
from key import Key


class Constants:
    def __init__(self) -> None:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

            self.max_velocity = config["kinematics"]["maxvelocity"]
            self.max_acceleration = config["kinematics"]["maxacceleration"]

            first_key = config["standardkeylayout"]["88key"]["firstkey"]["pianokey"]
            first_note = config["standardkeylayout"]["88key"]["firstkey"]["midinote"]

            self.first_88_key = Key(first_note, int(first_key[1]), first_key[0], 0)

            first_key = config["standardkeylayout"]["76key"]["firstkey"]["pianokey"]
            first_note = config["standardkeylayout"]["76key"]["firstkey"]["midinote"]

            self.first_76_key = Key(first_note, int(first_key[1]), first_key[0], 0)

            first_key = config["standardkeylayout"]["61key"]["firstkey"]["pianokey"]
            first_note = config["standardkeylayout"]["61key"]["firstkey"]["midinote"]

            self.first_61_key = Key(first_note, int(first_key[1]), first_key[0], 0)

            first_key = config["standardkeylayout"]["49key"]["firstkey"]["pianokey"]
            first_note = config["standardkeylayout"]["49key"]["firstkey"]["midinote"]

            self.first_49_key = Key(first_note, int(first_key[1]), first_key[0], 0)

            self.base_18: tuple = tuple()
            self.step_list: tuple = tuple()
            self.__generate_base_18()
            self.__generate_step_list()

    def __generate_base_18(self) -> None:
        temp_list: list[str] = []
        for i in range(0, 10):
            temp_list.append(str(i))
        for i in range(ord("A"), ord("H") + 1):
            temp_list.append(chr(i))
        self.base_18 = tuple(temp_list)

    def __generate_step_list(self) -> None:
        temp_list: list[str] = []
        for i in range(ord("A"), ord("G") + 1):
            temp_list.append(chr(i))
        self.step_list = tuple(temp_list)


"""
top = None
bottom = None
allValues = []
index = 0
beginningOffset = 0
keyPositions = [None] * 8

# Run through all 88 possible whole step keys and mapping the solenoids able to play each note. None means not playable
for x, key in enumerate(positions):
    # Until we hit the start key every key is assigned all None values
    if key == startKey:
        # For each key processed there are that many less keys left on the keybaord and doubly so when sharps are concerned see above
        keyCount -= tempCount
        # Keys are processed left to right are playable and new playable positions start from the furthest left and farthest left solenoid gets repalces
        keyPositions.pop(-1)
        keyPositions.insert(0, x)
        # Once a key is processed if the end of keyboard is not reached then the next key is set to be processed
        if (x + 1) != len(positions):
            startKey = positions[x + 1]
        # index += 1
    else:
        # Keeps track of where the solenoid assignment starts
        beginningOffset += 1
    # The figured positions are assigned to the list of notes
    notes[x] = keyPositions.copy()

while (index + 1) < len(positions):
    index += 1
    j = 0
    while j <= endOffset:
        notes[index][j] = None
        j += 1
    if endOffset < 7:
        endOffset += 1


"""
