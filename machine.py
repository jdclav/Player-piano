from curses import wrapper
from decode import CommandList
import time
from frame import FrameList


def main(stdscr):
    # 1 for anything other than testing
    speedMultiply = 1

    path = "results.pcode"

    command_list = CommandList(path)

    frame_list = FrameList()

    frame_list.process_command_list(command_list)

    startTime = round(time.time() * 1000)

    currentTime = startTime

    for frame in frame_list.frames:
        while (currentTime - startTime) < (frame.frame_time / speedMultiply):
            currentTime = round(time.time() * 1000)

        stdscr.addstr(0, 0, "".join(frame.topLine))
        stdscr.addstr(1, 0, "".join(frame.middleLine))
        stdscr.addstr(2, 0, "".join(frame.bottomLine))

        stdscr.refresh()

    stdscr.getch()


wrapper(main)
