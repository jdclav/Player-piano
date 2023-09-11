from curses import wrapper
import pcode_decode
import time
import screen


def main(stdscr):
    # 1 for anything other than testing
    speedMultiply = 1

    path = "results.pcode"

    keyWidth = 22

    rightPosition = 1

    commandsList = pcode_decode.sorted_commandsList(path)

    startTime = round(time.time() * 1000)

    currentTime = startTime

    displayList = []

    for com in commandsList[0]:
        rightKeyDifference = (com[2] / keyWidth) - rightPosition

        frameList = screen.move_hand(rightKeyDifference, rightPosition, 0, com[3])

        rightPosition = int(com[2] / keyWidth)

        displayList = displayList + frameList

    dDisplayList = []

    for com in commandsList[1]:
        x = 0

        for display in displayList:
            if com[4] > display[1]:
                x = x + 1

        dDisplayList.append(
            [
                screen.actuate(displayList[x - 1][0], displayList[x - 1][2], com[2]),
                com[4],
            ]
        )
        dDisplayList.append(
            [
                screen.retract(dDisplayList[-1][0], displayList[x - 1][2]),
                com[4] + com[5],
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
