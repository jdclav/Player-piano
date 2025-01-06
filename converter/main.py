import os
from constants import Constants
from converter.procsss_xml import MusicXML
from playable import PlayableNoteList
from solenoids import SolenoidIndex
from pcode import PlayList, MoveList, Hand

# TODO temp constants
RETRACT_TIME = 50000
KEY_WIDTH = 23.2
FILE_NAME = "/testing.pcode"

constants = Constants()

key_map = SolenoidIndex(88, constants.first_88_key)

current_directory = os.path.dirname(os.path.realpath(__file__))
file_name = "test.musicxml"

xml_file = f"{current_directory}/{file_name}"

music_xml = MusicXML(xml_file)

first_part = music_xml.part_ids[0]

first_staff = music_xml.generate_note_list(first_part)[0]

music_xml.us_per_division(first_part.id)

note_list = PlayableNoteList(key_map, first_staff)

note_list.find_groups()
note_list.find_clusters()
note_list.set_tick_duration(music_xml.us_per_div)
note_list.find_moves(23.2, constants.max_acceleration, constants.max_velocity)
note_list.find_locations()
note_list.find_time_losses()

play_commands = PlayList(note_list, key_map, music_xml.us_per_div)
play_commands.generate_play_list(Hand.RIGHT)

move_commands = MoveList(note_list, key_map, music_xml.us_per_div)
move_commands.generate_move_list(Hand.RIGHT, KEY_WIDTH, RETRACT_TIME)

full_pcode = f"s\n{play_commands}{move_commands}e"

write_path = os.path.dirname(os.path.realpath(__file__)) + FILE_NAME

with open(write_path, "wt") as f:
    f.write(full_pcode)


# TODO NEXT Find out why the start position is not correct.
