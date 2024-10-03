import os
import yaml
from key import Key


class Constants:
    def __init__(self) -> None:
        current_directory = os.path.dirname(os.path.realpath(__file__))
        file_name = "config.yaml"

        full_path = f"{current_directory}/{file_name}"

        with open(full_path, "r") as file:
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
