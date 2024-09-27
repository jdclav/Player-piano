import os

from musicxml import MusicXML

# TODO Should be replaced by user input
current_directory = os.path.dirname(os.path.realpath(__file__))
file_name = "test.musicxml"

xml_file = f"{current_directory}/{file_name}"

music_xml = MusicXML(xml_file)


"""for items in note_list:
    print(
        "=================================================================================================="
    )
    for item in items:
        print(item)"""
