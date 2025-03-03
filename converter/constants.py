import os
import yaml
from key import Key


class Constants:
    def __init__(self) -> None:
        """
        This will read from a file "config.yaml" that exists in the same directory.
        It will extract the values selected in that file and expose the data in the resulting object.
        """
        current_directory = os.path.dirname(os.path.realpath(__file__))
        file_name = "config.yaml"

        full_path = f"{current_directory}/{file_name}"

        with open(full_path, "r") as file:
            config = yaml.safe_load(file)
            self.max_velocity = config["kinematics"]["maxvelocity"]
            """The max velocity for all calculations tied to this config."""

            self.max_acceleration = config["kinematics"]["maxacceleration"]
            """The default acceleration for all calcuations tied to this config."""

            first_key = config["standardkeylayout"]["88key"]["firstkey"]["pianokey"]
            first_note = config["standardkeylayout"]["88key"]["firstkey"]["midinote"]
            self.first_88_key = Key(first_note, int(first_key[1]), first_key[0], 0)
            """This will be the first key on an 88 key piano"""

            first_key = config["standardkeylayout"]["76key"]["firstkey"]["pianokey"]
            first_note = config["standardkeylayout"]["76key"]["firstkey"]["midinote"]
            self.first_76_key = Key(first_note, int(first_key[1]), first_key[0], 0)
            """This will be the first key on a 76 key piano"""

            first_key = config["standardkeylayout"]["61key"]["firstkey"]["pianokey"]
            first_note = config["standardkeylayout"]["61key"]["firstkey"]["midinote"]
            self.first_61_key = Key(first_note, int(first_key[1]), first_key[0], 0)
            """This will be the first key on a 61 key piano"""

            first_key = config["standardkeylayout"]["49key"]["firstkey"]["pianokey"]
            first_note = config["standardkeylayout"]["49key"]["firstkey"]["midinote"]
            self.first_49_key = Key(first_note, int(first_key[1]), first_key[0], 0)
            """This will be the first key on a 49 key piano"""

            self.base_18: tuple = tuple()
            """TODO unused A tuple that will return the base18 digit converted from the base10 index."""

            self.step_list: tuple = tuple()
            """TODO unused and unclear its use case."""

            self.__generate_step_list()

    def __generate_step_list(self) -> None:
        """TODO unsure."""

        temp_list: list[str] = []

        for i in range(ord("A"), ord("G") + 1):
            temp_list.append(chr(i))

        self.step_list = tuple(temp_list)


def base_18() -> tuple[str]:
    """Generates a tuple where each base10 index maps to the appropirate base18 digit."""

    temp_list: list[str] = []

    for i in range(0, 10):
        temp_list.append(str(i))

    for i in range(ord("A"), ord("H") + 1):
        temp_list.append(chr(i))

    return tuple(temp_list)
