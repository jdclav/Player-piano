import os

from musicxml import MusicXML, NoteList


def find_still_groups(note_list: NoteList) -> list[NoteList]:
    temp_group = NoteList(note_list.part_id, note_list.staff_number)

    for note in note_list:
        if not temp_group.notes:
            temp_group.append(note)

        else:
            new_group = set(temp_group.notes).intersection()


if __name__ == "__main__":
    # TODO Should be replaced by user input
    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_name = "test.musicxml"

    xml_file = f"{current_directory}/{file_name}"

    music_xml = MusicXML(xml_file)

    first_part = music_xml.part_ids[1]

    first_staff = music_xml.generate_note_list(first_part)

    find_still_groups(first_staff[0])
