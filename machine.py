from curses import wrapper
import pcode_decode
import time
import screen


def main(stdscr):
    # 1 for anything other than testing
    speedMultiply = 1

    path = "results.pcode"

    key_width = 22

    right_hand_position = 1

    commandsList = pcode_decode.sorted_commandsList(path)

    startTime = round(time.time() * 1000)

    currentTime = startTime

    displayList = []

    for com in commandsList[0]:
        distance_in_keys = (com.position / key_width) - right_hand_position

        frameList = screen.move_hand(distance_in_keys, right_hand_position, 0, com.duration)

        right_hand_position = int(com.position / key_width)

        displayList = displayList + frameList

    dDisplayList = []

    for com in commandsList[1]:
        x = 0

        for display in displayList:
            if com.duration > display[1]:
                x = x + 1

        dDisplayList.append(
            [
                screen.actuate(displayList[x - 1][0], displayList[x - 1][2], com.solenoid_locations),
                com.duration,
            ]
        )
        dDisplayList.append(
            [
                screen.retract(dDisplayList[-1][0], displayList[x - 1][2]),
                com.duration + com.longevity,
            ]
        )

    displayList = displayList + dDisplayList

    displayList.sort(key=lambda x: x[1])

    for display in displayList:
        while (currentTime - startTime) < (display[1] / speedMultiply):
            currentTime = round(time.time() * 1000)

        stdscr.addstr(0, 0, "".join(display[0][2]))
        stdscr.addstr(1, 0, "".join(display[0][1]))
        stdscr.addstr(2, 0, "".join(display[0][0]))

        stdscr.refresh()

    stdscr.getch()


wrapper(main)
