import os

from converter.musicxml_old import MusicXML, NoteList
from playable import PlayableNoteList
from solenoids import SolenoidIndex
from constants import Constants


if __name__ == "__main__":
    # TODO Should be replaced by user input
    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_name = "test.musicxml"
    constants = Constants()
    key_map = SolenoidIndex(88, constants.first_88_key)

    xml_file = f"{current_directory}/{file_name}"

    music_xml = MusicXML(xml_file)

    first_part = music_xml.part_ids[1]

    first_staff = music_xml.generate_note_list(first_part)[0]

    playable_list = PlayableNoteList(key_map, first_staff)

    find_still_groups(playable_list)
