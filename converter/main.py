import os
from constants import Constants
from procsss_xml import MusicPiece
from playable import StillNotesList
from solenoids import SolenoidIndex
from pcode import PlayList, MoveList, Hand

# TODO temp constants
RETRACT_TIME = 50000
KEY_WIDTH = 23.2
FILE_NAME = "/testing.pcode"


constants = Constants()

key_map = SolenoidIndex(88, constants.first_88_key)

current_directory = os.path.dirname(os.path.realpath(__file__))
file_name = "moonlight.musicxml"
# file_name = "test.musicxml"

xml_file = f"{current_directory}/{file_name}"

processed_xml = MusicPiece(xml_file)

score_part = processed_xml.parts_list[0]

note_list = StillNotesList(key_map, processed_xml, score_part, 1)

note_list.find_groups()
note_list.find_clusters()
note_list.find_moves(KEY_WIDTH, constants.max_acceleration, constants.max_velocity)
note_list.find_locations()
note_list.find_time_losses()

play_commands = PlayList(note_list, key_map)
play_commands.generate_play_list(Hand.RIGHT)

move_commands = MoveList(note_list, key_map)
move_commands.generate_move_list(Hand.RIGHT, 23.2, 1000)

full_pcode = f"s\n{play_commands}{move_commands}e"

write_path = os.path.dirname(os.path.realpath(__file__)) + FILE_NAME

with open(write_path, "wt") as f:
    f.write(full_pcode)


# TODO NEXT Find out why the start position is not correct.
