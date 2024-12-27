from curses import wrapper
from decode import CommandList
import time
import simpleaudio as sa
from frame import FrameList
from audioTest import NoteList
import os

SAMPLE_RATE = 48000
SPEED_MULTIPLIER = 1


def main(stdscr):

    current_directory = os.path.dirname(os.path.realpath(__file__))
    file = "/testing.pcode"

    command_list = CommandList(current_directory + file)
    frame_list = FrameList()
    frame_list.process_command_list(command_list)
    notes = NoteList()

    for frame in frame_list.audio_frames:
        for note in frame.midi_notes:
            notes.add_note(note, frame.frame_start, frame.duration, 10)

    for i, note in enumerate(notes.note_list):
        if note.duration < 0:
            print("Index: " + str(i) + " " + str(note))

    notes.full_waveform(frame_list.piano_state.frame_time, 1000, SAMPLE_RATE)
    sa.play_buffer(notes.waveform, 1, 2, SAMPLE_RATE)

    startTime = round(time.time() * 1000)
    currentTime = startTime

    for frame in frame_list.frames:
        while (currentTime - startTime) < (frame.frame_time / SPEED_MULTIPLIER):
            currentTime = round(time.time() * 1000)

        stdscr.addstr(0, 0, "".join(frame.topLine))
        stdscr.addstr(1, 0, "".join(frame.middleLine))
        stdscr.addstr(2, 0, "".join(frame.bottomLine))

        stdscr.refresh()

    stdscr.getch()


wrapper(main)
