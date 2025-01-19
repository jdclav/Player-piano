from curses import wrapper
from decode import CommandList
import time
import simpleaudio as sa
from frame import FrameList
from audioTest import NoteList

SAMPLE_RATE = 48000


def main(stdscr):
    # 1 for anything other than testing
    speedMultiply = 1

    path = "testing.pcode"

    command_list = CommandList(path)

    frame_list = FrameList()

    frame_list.process_command_list(command_list)

    notes = NoteList()

    for frame in frame_list.audio_frames:
        for note in frame.midi_notes:
            notes.add_note(
                note, frame.frame_start, frame.duration, frame.frame_velocity
            )

    for i, note in enumerate(notes.note_list):
        if note.duration < 0:
            print("Index: " + str(i) + " " + str(note))

    notes.full_waveform(frame_list.piano_state.frame_time, 1000, SAMPLE_RATE)

    sa.play_buffer(notes.waveform, 1, 2, SAMPLE_RATE)

    startTime = round(time.time() * 1000)

    currentTime = startTime

    for i, frame in enumerate(frame_list.frames):
        currentTime = round(time.time() * 1000)
        while (currentTime - startTime) < (frame.frame_time / speedMultiply):
            currentTime = round(time.time() * 1000)

        stdscr.addstr(0, 0, "".join(frame.topLine))
        stdscr.addstr(1, 0, "".join(frame.middleLine))
        stdscr.addstr(2, 0, "".join(frame.bottomLine))

        stdscr.refresh()

    stdscr.getch()


wrapper(main)
