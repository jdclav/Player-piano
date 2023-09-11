import kinematics
import numpy
from copy import deepcopy

closedSolenoidChar = "\u03A6"
openSolenoidChar = "\U0000039F"
keyChar = "\U0000203E"
keyPlayedChar = "\U00002534"
keyWidth = 22

keyCount = 76
screenOffset = 13


def pianoSetup():
    whiteKeysIndex = []
    blackKeysIndex = []

    whiteSolenoidIndex = []
    blackSolenoidIndex = []

    indexs = (whiteKeysIndex, blackKeysIndex, whiteSolenoidIndex, blackSolenoidIndex)

    missingKey = 2

    for x in range(keyCount + screenOffset + 1):
        if x % 2:
            blackSolenoidIndex.append(x)
            if missingKey != 2 and missingKey != 6:
                blackKeysIndex.append(x)
            missingKey += 1
            if missingKey == 7:
                missingKey = 0

        else:
            whiteKeysIndex.append(x)
            whiteSolenoidIndex.append(x)

    blackKeysIndex.pop()

    return indexs


indexs = pianoSetup()


def defaultScreen():
    bottomLine = [" "] * (keyCount + screenOffset)
    middleLine = [" "] * (keyCount + screenOffset)
    topLine = [" "] * (keyCount + screenOffset)

    screen = [bottomLine, middleLine, topLine]

    for x in indexs[0]:
        bottomLine[x] = keyChar

    for x in indexs[1]:
        middleLine[x] = keyChar

    return screen


def populateHand(screen, location: int, hand: int):
    solenoids = [None] * 16
    solenoidOffset = 1

    whiteSolenoidIndex = indexs[2]
    blackSolenoidIndex = indexs[3]

    middleLine = screen[1]
    topLine = screen[2]

    for x in range(8):
        whiteSolenoid = whiteSolenoidIndex[x + location]
        blackSolenoid = blackSolenoidIndex[x + location - solenoidOffset + hand]
        middleLine[whiteSolenoid] = closedSolenoidChar
        solenoids[x] = whiteSolenoid
        topLine[blackSolenoid] = closedSolenoidChar
        solenoids[x + 8] = blackSolenoid

    return solenoids


def actuate(screen, solenoids, press):
    screenCopy = deepcopy(screen)

    whiteKeysLine = screenCopy[0]
    whiteSolenoidsLine = screenCopy[1]

    blackKeysLine = screenCopy[1]
    blackSolenoidsLine = screenCopy[2]

    for x in press:
        if x is not None:
            if x < 8:
                whiteKeysLine[solenoids[x]] = keyPlayedChar
                whiteSolenoidsLine[solenoids[x]] = openSolenoidChar
            elif x < 16:
                blackKeysLine[solenoids[x]] = keyPlayedChar
                blackSolenoidsLine[solenoids[x]] = openSolenoidChar

    return screenCopy


def retract(screen, solenoids):
    screenCopy = deepcopy(screen)

    blackKeysIndex = indexs[1]

    bottomLine = screenCopy[0]
    middleLine = screenCopy[1]
    topLine = screenCopy[2]

    line = 0

    for x in solenoids:
        if line < 8:
            bottomLine[x] = keyChar
            middleLine[x] = closedSolenoidChar
        elif line < 16:
            if x in blackKeysIndex:
                middleLine[x] = keyChar
            topLine[x] = closedSolenoidChar
        line += 1
    return screenCopy


def move_hand(distance, location, hand, timeOffset):
    locationTimes = kinematics.timeDistanceList(22, 3000, 300, abs(distance))

    frameList = [None] * len(locationTimes)

    for i in range(len(locationTimes)):
        frameList[i] = [defaultScreen(), locationTimes[i] + timeOffset]

        solenoid = populateHand(
            frameList[i][0], int((i * numpy.sign(distance)) + location), hand
        )

        frameList[i].append(solenoid)

    return frameList
