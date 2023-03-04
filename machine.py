import curses
import time
import math
from curses import wrapper

rightHand = 0
leftHand = 0

closedSolenoidChar = '\u03A6'
openSolenoidChar = '\U0000039F'
keyChar = '\U0000203E'
keyPlayedChar = '\U00002534'


handWidth = 8
rightHandSize = 0
leftHandSize = 0

keyWidth = 23.2

def timeDistanceAcceleration(distance, acceleration):
    return math.sqrt((2 * distance) / acceleration)

def timeDistanceVelocity(distance, velocity, distanceOffset, timeOffset):
    return ((distance - distanceOffset) / velocity) + timeOffset

def timeDistanceDeceleration(distance, velocity, acceleration, distanceOffset, timeOffset):
    squareRoot = math.sqrt((velocity ** 2) - (2 * acceleration * (distance - distanceOffset)))
    return ((velocity - squareRoot) / acceleration) + timeOffset

def timeDistanceFunction(distance, acceleration, maxVelocity, totalDistance):
    timeToVelocity = (maxVelocity / acceleration)
    distanceToVelocity = (0.5 * acceleration * (timeToVelocity ** 2))

    timePoint = 0

    # totalDistance is the total distance traveled for this calculation so any distance greater than
    # that would be out of scope.
    if((distance > totalDistance) or (distance < 0)):
        return timePoint

    if((2 * distanceToVelocity) > totalDistance):
        halfDistance = totalDistance / 2
        timeOffset = math.sqrt((2 * halfDistance) / acceleration) 
        if(distance < halfDistance):
            timePoint = timeDistanceAcceleration(distance, acceleration)
        else:
            timePoint = timeDistanceDeceleration(distance, maxVelocity, acceleration, halfDistance, 
                                            timeOffset)
    else:
        distanceToDeceleration = totalDistance - distanceToVelocity
        
        if(distance < distanceToVelocity):
            timePoint = timeDistanceAcceleration(distance, acceleration)
        elif(distance < distanceToDeceleration):
            timePoint = timeDistanceVelocity(distance, maxVelocity, distanceToVelocity, 
                                               timeToVelocity)
        else:
            timeToDeceleration = timeDistanceVelocity(distanceToDeceleration, maxVelocity, 
                                                  distanceToVelocity, timeToVelocity)
            
            timePoint = timeDistanceDeceleration(distance, maxVelocity, acceleration, 
                                            distanceToDeceleration, timeToDeceleration)

    return 1000 * (timePoint)    
    
def timeDistanceList(distanceInterval, acceleration, maxVelocity, totalDistance): 
    adjustedAcceleration = (acceleration / distanceInterval)
    adjustedVelocity = (maxVelocity / distanceInterval)
    adjustedTotalDistance = (totalDistance / distanceInterval)

    positions = []
    
    for i in range(int(adjustedTotalDistance) + 1):
        positions.append([(distanceInterval * i), 
                          timeDistanceFunction(i, adjustedAcceleration, adjustedVelocity, 
                                               adjustedTotalDistance)])
    
    return positions
        

def pianoSetup():

    whiteKeysIndex = []
    blackKeysIndex = []

    whiteSolenoidIndex = []
    blackSolenoidIndex = []

    indexs = (whiteKeysIndex, blackKeysIndex, whiteSolenoidIndex, blackSolenoidIndex)

    missingKey = 2

    for x in range(90):
        if(x % 2):
            blackSolenoidIndex.append(x)
            if(missingKey != 2 and missingKey != 6):
                blackKeysIndex.append(x)
            missingKey += 1
            if(missingKey == 7):
                missingKey = 0

        else:
            whiteKeysIndex.append(x)
            whiteSolenoidIndex.append(x)

    blackKeysIndex.pop()

    return indexs

def defaultScreen(indexs):

    bottomLine = [' '] * 89
    middleLine = [' '] * 89
    topLine = [' '] * 89

    screen = (bottomLine, middleLine, topLine)

    for x in indexs[0]:
        bottomLine[x] = keyChar

    for x in indexs[1]:
        middleLine[x] = keyChar

    return screen

def populateLeftHand(indexs, screen, location):

    solenoids = [None] * 16

    whiteSolenoidIndex = indexs[2]
    blackSolenoidIndex = indexs[3]

    middleLine = screen[1]
    topLine = screen[2]

    for x in range(8):
        whiteSolenoid = whiteSolenoidIndex[x + location]
        blackSolenoid = blackSolenoidIndex[x + location]
        middleLine[whiteSolenoid] = closedSolenoidChar
        solenoids[x] = whiteSolenoid
        topLine[blackSolenoid] = closedSolenoidChar
        solenoids[x + 8] = blackSolenoid

    return screen, solenoids


def populateRightHand(indexs, screen, location):

    solenoids = [None] * 16

    whiteSolenoidIndex = indexs[2]
    blackSolenoidIndex = indexs[3]

    middleLine = screen[1]
    topLine = screen[2]

    for x in range(8):
        whiteSolenoid = whiteSolenoidIndex[x + location]
        blackSolenoid = blackSolenoidIndex[x + location - 1]
        middleLine[whiteSolenoid] = closedSolenoidChar
        solenoids[x] = whiteSolenoid
        topLine[blackSolenoid] = closedSolenoidChar
        solenoids[x + 8] = blackSolenoid

    return screen, solenoids


def actuate(screen, solenoids, press):

    whiteKeysLine = screen[0]
    whiteSolenoidsLine = screen[1]

    blackKeysLine = screen[1]
    blackSolenoidsLine = screen[2]

    for x in press:
        if(x != None):
            if(x < 8):
                whiteKeysLine[solenoids[x]] = keyPlayedChar
                whiteSolenoidsLine[solenoids[x]] = openSolenoidChar
            elif(x < 16):
                blackKeysLine[solenoids[x]] = keyPlayedChar
                blackSolenoidsLine[solenoids[x]] = openSolenoidChar
    
    return screen

def retract(indexs, screen, solenoids):
    
    blackKeysIndex = indexs[1]
    
    bottomLine = screen[0]   
    middleLine = screen[1]
    topLine = screen[2]

    line = 0

    for x in solenoids:
        if (line < 8):
            bottomLine[x] = keyChar
            middleLine[x] = closedSolenoidChar
        elif (line < 16):
            if(x in blackKeysIndex):
                middleLine[x] = keyChar
            topLine[x] = closedSolenoidChar
        line += 1


def clearKeys(indexs, screen):
    whiteKeysIndex = indexs[0]
    blackKeysIndex = indexs[1]

    bottomLine = screen[0]
    middleLine = screen[1]
    
    for x in whiteKeysIndex:
        bottomLine[x] = keyChar
    
    for x in blackKeysIndex:
        middleLine[x] = keyChar


def main(stdscr):

    startTime = round(time.time() * 1000)

    currentTime = startTime

    stdscr.clear()

    press = [0, 2, 5]

    indexs = pianoSetup()

    display = defaultScreen(indexs)

    display, rightSolenoids = populateRightHand(indexs, display, 1)

    stdscr.addstr(0,0,''.join(display[2]))
    stdscr.addstr(1,0,''.join(display[1]))
    stdscr.addstr(2,0,''.join(display[0]))
    
    stdscr.refresh()

    while((currentTime - startTime) < 3000):

        currentTime = round(time.time() * 1000)

        if((currentTime - startTime) > 1000 and (currentTime - startTime) < 2000):

            actuate(display, rightSolenoids, press)

        if((currentTime - startTime) > 2000):

            retract(indexs, display, rightSolenoids)
        
        stdscr.addstr(0,0,''.join(display[2]))
        stdscr.addstr(1,0,''.join(display[1]))
        stdscr.addstr(2,0,''.join(display[0]))
        
        stdscr.refresh()

    stdscr.getch()

wrapper(main)