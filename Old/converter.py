#!/usr/bin/env python3
from pathlib import Path
import argparse
import math
import sys


# Distance time cost function
def travel_time(distance, accel, velocity):
    mAccelDistance = (velocity**2) / (2 * accel)
    if mAccelDistance > distance:
        rDistance = 0
        accelDistance = distance
    else:
        accelDistance = mAccelDistance
        rDistance = distance - accelDistance

    accelTime = 2 * math.sqrt(accelDistance / (accel))
    linearTime = rDistance / velocity
    totalTime = accelTime + linearTime
    return totalTime * 1000


# List to convert decimal to base 17
base17 = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
]

# Lists of each note and which solenoids can play the note at a given position
A0 = [0, None, None, None, None, None, None, None]
B0 = [1, 0, None, None, None, None, None, None]
C1 = [2, 1, 0, None, None, None, None, None]
D1 = [3, 2, 1, 0, None, None, None, None]
E1 = [4, 3, 2, 1, 0, None, None, None]
F1 = [5, 4, 3, 2, 1, 0, None, None]
G1 = [6, 5, 4, 3, 2, 1, 0, None]
A1 = [7, 6, 5, 4, 3, 2, 1, 0]
B1 = [8, 7, 6, 5, 4, 3, 2, 1]
C2 = [9, 8, 7, 6, 5, 4, 3, 2]
D2 = [10, 9, 8, 7, 6, 5, 4, 3]
E2 = [11, 10, 9, 8, 7, 6, 5, 4]
F2 = [12, 11, 10, 9, 8, 7, 6, 5]
G2 = [13, 12, 11, 10, 9, 8, 7, 6]
A2 = [14, 13, 12, 11, 10, 9, 8, 7]
B2 = [15, 14, 13, 12, 11, 10, 9, 8]
C3 = [16, 15, 14, 13, 12, 11, 10, 9]
D3 = [17, 16, 15, 14, 13, 12, 11, 10]
E3 = [18, 17, 16, 15, 14, 13, 12, 11]
F3 = [19, 18, 17, 16, 15, 14, 13, 12]
G3 = [20, 19, 18, 17, 16, 15, 14, 13]
A3 = [21, 20, 19, 18, 17, 16, 15, 14]
B3 = [22, 21, 20, 19, 18, 17, 16, 15]
C4 = [23, 22, 21, 20, 19, 18, 17, 16]
D4 = [24, 23, 22, 21, 20, 19, 18, 17]
E4 = [25, 24, 23, 22, 21, 20, 19, 18]
F4 = [26, 25, 24, 23, 22, 21, 20, 19]
G4 = [27, 26, 25, 24, 23, 22, 21, 20]
A4 = [28, 27, 26, 25, 24, 23, 22, 21]
B4 = [29, 28, 27, 26, 25, 24, 23, 22]
C5 = [30, 29, 28, 27, 26, 25, 24, 23]
D5 = [31, 30, 29, 28, 27, 26, 25, 24]
E5 = [32, 31, 30, 29, 28, 27, 26, 25]
F5 = [33, 32, 31, 30, 29, 28, 27, 26]
G5 = [34, 33, 32, 31, 30, 29, 28, 27]
A5 = [35, 34, 33, 32, 31, 30, 29, 28]
B5 = [36, 35, 34, 33, 32, 31, 30, 29]
C6 = [37, 36, 35, 34, 33, 32, 31, 30]
D6 = [38, 37, 36, 35, 34, 33, 32, 31]
E6 = [39, 38, 37, 36, 35, 34, 33, 32]
F6 = [40, 39, 38, 37, 36, 35, 34, 33]
G6 = [41, 40, 39, 38, 37, 36, 35, 34]
A6 = [42, 41, 40, 39, 38, 37, 36, 35]
B6 = [43, 42, 41, 40, 39, 38, 37, 36]
C7 = [44, 43, 42, 41, 40, 39, 38, 37]
D7 = [None, 44, 43, 42, 41, 40, 39, 38]
E7 = [None, None, 44, 43, 42, 41, 40, 39]
F7 = [None, None, None, 44, 43, 42, 41, 40]
G7 = [None, None, None, None, 44, 43, 42, 41]
A7 = [None, None, None, None, None, 44, 43, 42]
B7 = [None, None, None, None, None, None, 44, 43]
C8 = [None, None, None, None, None, None, None, 44]
R = list(range(1, 44))

# List of all the notes with there respective list
notes = [
    A0,
    B0,
    C1,
    D1,
    E1,
    F1,
    G1,
    A1,
    B1,
    C2,
    D2,
    E2,
    F2,
    G2,
    A2,
    B2,
    C3,
    D3,
    E3,
    F3,
    G3,
    A3,
    B3,
    C4,
    D4,
    E4,
    F4,
    G4,
    A4,
    B4,
    C5,
    D5,
    E5,
    F5,
    G5,
    A5,
    B5,
    C6,
    D6,
    E6,
    F6,
    G6,
    A6,
    B6,
    C7,
    D7,
    E7,
    F7,
    G7,
    A7,
    B7,
    C8,
    R,
]
"""
List that contains lists of values for solenoid playable mapping.
"""

# Parallel list which has the notes name as a string
positions = [
    "A0",
    "B0",
    "C1",
    "D1",
    "E1",
    "F1",
    "G1",
    "A1",
    "B1",
    "C2",
    "D2",
    "E2",
    "F2",
    "G2",
    "A2",
    "B2",
    "C3",
    "D3",
    "E3",
    "F3",
    "G3",
    "A3",
    "B3",
    "C4",
    "D4",
    "E4",
    "F4",
    "G4",
    "A4",
    "B4",
    "C5",
    "D5",
    "E5",
    "F5",
    "G5",
    "A5",
    "B5",
    "C6",
    "D6",
    "E6",
    "F6",
    "G6",
    "A6",
    "B6",
    "C7",
    "D7",
    "E7",
    "F7",
    "G7",
    "A7",
    "B7",
    "C8",
    "R",
]

# Variables for configuration
# Kinemtatic Variables
maxSpeed = 300
maxAccel = 3000
# Keyboard variable
keyWidth = 23.2
keyCount = 76
startKey = "E1"
# Timing variables
actuationTime = 50
prePlay = 5000
preMove = 100

# Variable the represents the file being read
# THIS IS WHAT TO MODIFY SEBASTIAN v


### THIS IS WHAT TO MODIFY SEBASTIAN ###
music_path = str(("music.txt"))
print(f"Compiling Music File: {music_path}")

with open(music_path, mode="r", encoding="utf-8") as f:
    mNote = f.read()
# f.close()

# Create a list of each item in the file string delimited by a space
mNoteSpace = mNote.split(" ")

# Assign the tempo based on the item at index 1
tempo = mNoteSpace[1]

# The time signiture is collected from index 2 and broken into the top and bottom value
timeSig = mNoteSpace[2].split("/")

# Whether the music is for the left or right hand
hand = mNoteSpace[0]

# Finds the note used to referance tempo
noteType = int(timeSig[1])

# finds the notes per second
beatDuration = 60 / int(tempo)

# These are all the notes that will be played
playable = mNoteSpace[3:]

# creates a list with a size equal to the playable notes
values = [None] * len(playable)
"""Will hold numeric(still str) versions of everything listed in playable. Note PITCH.OCTAVE is converter to key location/index"""

# The duration of a whole note
noteDuration = round(noteType * beatDuration * 1000)

# Identify which hand the music is for
if hand == "R":
    handedness = 0
elif hand == "L":
    handedness = 1
else:
    sys.exit("The input file is not correct")


###############################################################################################################################################################

# Variables used in processing to map the keyboard and playable notes based on number of keys and starting key
top = None
bottom = None
allValues = []
"""Holds the integer note type of each note."""
index = 0
beginningOffset = 0
keyPositions = [None] * 8

# Run through all 88 possible whole step keys and mapping the solenoids able to play each note. None means not playable
for x, key in enumerate(positions):
    # keyCount is subtracted for each run of the loop
    if keyCount <= 0:
        break
    # B and E notes have no sharps meaning the represent only 1 key
    if (key[0] == "B") | (key[0] == "E"):
        tempCount = 1
    # Keys other than B and E have sharps therefore they have 2 keys to represent them
    else:
        tempCount = 2

    # Until we hit the start key every key is assigned all None values
    if key == startKey:
        # For each key processed there are that many less keys left on the keybaord and doubly so when sharps are concerned see above
        keyCount -= tempCount
        # Keys are processed left to right are playable and new playable positions start from the furthest left and farthest left solenoid gets repalces
        keyPositions.pop(-1)
        keyPositions.insert(0, x)
        # Once a key is processed if the end of keyboard is not reached then the next key is set to be processed
        if (x + 1) != len(positions):
            startKey = positions[x + 1]
        # index += 1
    else:
        # Keeps track of where the solenoid assignment starts
        beginningOffset += 1
    # The figured positions are assigned to the list of notes
    notes[x] = keyPositions.copy()

# Assigning an index to 8 less than the end of the key assignment
index = x - 8

# Variable used in following processing to keep track of how many runs of the loop have occured
endOffset = 0

# Correct the last 8 positions since they have restricted playability
while (index + 1) < len(positions):
    index += 1
    j = 0
    while j <= endOffset:
        notes[index][j] = None
        j += 1
    if endOffset < 7:
        endOffset += 1


#########################################################################################################

# Variables used in following processing
sharp = []
"""Holds either a 1 or 0 to denote whether the playable note that aligns to the same index is a half step higher"""
rest = []
"""Holds either a 1 or 0 to denote whether the playable note that aligns to the same index is a rest"""
# Break playable notes into both note and pitch values
for x, note in enumerate(playable):
    value = note.split("/")
    """List with the pitch and note type"""

    if value[1].find("S") != -1:
        sharp.append(1)
        value[1] = value[1][0] + value[1][2]
    else:
        sharp.append(0)

    if value[1].find("R") != -1:
        rest.append(1)
    else:
        rest.append(0)

    check_index = value[1].strip()
    place = positions.index(check_index)
    """Map the note in value to the corrisponding index/location on the piano"""

    if handedness == 0:
        value_pair = [value[0], place + sharp[-1]]
    else:
        value_pair = [value[0], place]

    values[x] = value_pair

    allValues.append(int(value[0]))

# Variable used in next processing stage

# Identify all possible notes durations played
possibleValues = list(set(allValues))
possibleValues.sort()
noteScores = []
scores = []

#########################################################################################################

# vvv Not yet completed

# Assign a score with lower meaning better based on a cost function based on how many keys are moved to each played note. Score of 1 or more means the note cannot be played
for x, part in enumerate(possibleValues):
    noteTime = noteDuration / part
    score = 0
    keys = 0
    while score < 1:
        mTime = travel_time((keys * keyWidth), maxAccel, maxSpeed)
        score = mTime / noteTime
        scores.append(score)
        keys = keys + 1
    noteScores.append([part, scores])
    scores = []

###################################################################################

# Variables used in next processing step
places = []
"""
Stores each key position from each note
"""
spots = []
"""
Holds the first key index/location then each key index less than the last for the group
"""
locate = []
"""
Holds the first key index/location then each key index more than the last for the group
"""
compare = []
contrast = []
playList = []
"""
Most recent confirmed valid set of hand positions that are valid to play all the notes in playSet
"""
playSet = []
"""
Groups of notes that can be played without moving.
"""
changes = []
"""
For each note holds the number of keys that can be moved to the left after playing the note # MAYBE
"""
adjust = []
"""
For each note holds the number of keys that can be moved to the right after playing the note # MAYBE
"""
fowardChange = []
fowardAdjust = []
setValues = []
"""
Note type in the playSet
"""
# TODO

# Creates sets of playable notes with each set able to be played without any movement
for x, note in enumerate(values):
    changes.append(0)
    adjust.append(0)

    if not playList:
        places.append(values[x][1])  #
        playList = notes[values[x][1]]  #
        spots.append(places[x])  #
        locate.append(places[x])  #
        setValues.append(int(note[0]))  #
        continue

    hold = set(playList).intersection(notes[values[x][1]])
    """
    The current set of hand positions that are valid to play all the notes in PlayList plus the current note
    """

    if hold:
        places.append(values[x][1])
        setValues.append(int(note[0]))
        if places[-1] < spots[-1]:
            spots.append(places[-1])
            changes[-2] = spots[-1] - spots[-2]

        if places[-1] > locate[-1]:
            locate.append(places[-1])
            adjust[-2] = locate[-1] - locate[-2]

        playList = hold
        continue

    changes.pop()
    adjust.pop()

    top = max(playList)
    bottom = min(playList)
    playList = sorted(playList)
    playSet.append([playList.copy(), places.copy(), top, bottom, setValues])

    playList = []

    fowardChange.append(changes)
    """
    
    """
    fowardAdjust.append(adjust)
    """"
    
    """

    spots = []
    locate = []

    changes = []
    adjust = []

    places = []
    setValues = []
    places.append(values[x][1])
    setValues.append(int(note[0]))
    playList = notes[values[x][1]]
    spots.append(places[-1])
    locate.append(places[-1])
    changes.append(0)
    adjust.append(0)

top = max(playList)
bottom = min(playList)

playList = sorted(playList)
playSet.append([playList.copy(), places.copy(), top, bottom, setValues])
fowardChange.append(changes)
fowardAdjust.append(adjust)


################################################################################

# Variables used in nect processing step
setValues = []
places = []
spots = []
playList = []
compare = []
contrast = []
locate = []
changes = []
adjust = []
fullChange = []
fullAdjust = []


# Finds which notes in the group restrict right/left movement and by how many keys. Can use this to make preemtive moves.

for x, part in enumerate(playSet):
    if len(playSet) == 1:
        break

    compare = part[1].copy()
    compare.reverse()

    contrast = compare.copy()

    checks = set(compare)

    top = max(checks)
    bottom = min(checks)

    changes = [0] * len(compare)
    adjust = [0] * len(compare)

    # For every different pitch in the playable group
    for stuff in checks:
        # Find the note in the group that is the farthest right
        for z, spot in enumerate(compare):
            if spot == top:
                # A sorted list of each pitch in the compare group
                locate = sorted(list(set(compare)))

                # Replace the top value with the next largest value
                if len(locate) > 1:
                    top = locate[-2]

                # Remove all notes that occur after the current note for the next go around
                compare = compare[0:z]
                places.append([spot, z])
                # If there are multiple potential moves then record where/when a move can be made and by how many keys.
                if len(places) > 1:
                    changes[places[-2][1]] = places[-1][0] - places[-2][0]
                break

        # For every different pitch in the playable group
        for z, spot in enumerate(contrast):
            # Find the note in the group that is the farthest left
            if spot == bottom:
                # A sorted list of each pitch in the compare group
                locate = sorted(list(set(contrast)))

                # Replace the bottom value with the next smallest value
                if len(locate) > 1:
                    bottom = locate[1]

                # Remove all notes that occur after the current note for the next go around
                contrast = contrast[0:z]
                spots.append([spot, z])
                # If there are multiple potential moves then record where/when a move can be made and by how many keys.
                if len(spots) > 1:
                    adjust[spots[-2][1]] = spots[-1][0] - spots[-2][0]
                break
    places = []
    spots = []
    changes.reverse()
    adjust.reverse()
    fullChange.append(changes)
    fullAdjust.append(adjust)

# Variables used in next processing step
compare = []
finalPre = []
finalPost = []
locate = []


# Find which direction each group need to move from and to.

for x, part in enumerate(playSet):
    if not compare:
        compare = part
        finalPre.append([0])
        if len(playSet) == 1:
            locate.append(part[3])
        continue

    # Will the next move by right/left
    if part[3] > compare[3]:
        finalPre.append(fowardAdjust[x])
        finalPost.append(fullAdjust[x - 1])
        if not locate:
            locate.append(compare[2])
        locate.append([compare[2], part[3]])
        if len(playSet) == x + 1:
            locate.append(part[3])
            continue

    # Will the next move by right/left
    if part[3] < compare[3]:
        finalPre.append(fowardChange[x])
        finalPost.append(fullChange[x - 1])
        if not locate:
            locate.append(compare[3])
        locate.append([compare[3], part[2]])
        if len(playSet) == x + 1:
            locate.append(part[2])
            continue

    compare = part
finalPost.append([0])

compare = []

# TODO Determine the positions each group should start/end on. Not including premoves???

for x, part in enumerate(playSet):
    # If there is only a single playable group then there is no efficency improvment.
    if len(playSet) == 1:
        compare.append([0])
        break
    # If this is the first group
    if x == 0:
        compare.append([locate[0], locate[1][0]])
        continue
    # If this is the last group
    if len(playSet) == x + 1:
        compare.append([locate[x][1], locate[x + 1]])
        continue
    # else
    compare.append([locate[x][1], locate[x + 1][0]])

locate = compare.copy()


move = []

# TODO Find how much

for x, part in enumerate(locate):
    # No efficency for single group
    if len(playSet) == 1:
        break
    # How much should the first group move during playing.
    move.append([locate[x][1] - locate[x][0], 0])

    # If the last item then we are done.
    if (x + 1) == len(locate):
        continue
    # How much should the first group move to get to the next group.
    move[x][1] = locate[x + 1][0] - locate[x][1]

moveSet = []


# TODO This finds where each movement should occur based on a cost? function.

for x, place in enumerate(playSet):
    # Select items from playSet in reverse order.
    part = playSet[-1 * (x + 1)]
    if x == 0:
        prevPart = part
        continue

    preLength = move[-1 * (x + 1)][0]  # Movement in group
    postLength = move[-1 * (x + 1)][1]  # Movement after group
    totalLength = sum(move[-1 * (x + 1)])  # Total movement of pre and post move
    preChosen = []
    postChosen = []
    lastChosen = 0

    for i in range(0, abs(totalLength), 1):
        moveLocate = []

        preSum = abs(sum(finalPre[-1 * (x)]))  # Total pre movement in the group
        postSum = abs(move[-1 * (x + 1)][0])  # Total movement after the group

        preHeld = -1
        postHeld = -1
        postIndex = -1
        preIndex = -1
        preSelect = -1
        postSelect = -1

        currentIndex = -1
        bestLocate = -1

        specialMoves = 0

        bestScore = 1

        for j in range(0, len(prevPart[1]) - 1, 1): # for each note in the prePart group
            if (finalPre[-1 * (x)][j]) != 0: # If the pre movement allow movement
                preIndex = j
                if preSum > 0:
                    scoresList = []
                    for score in noteScores:
                        if score[0] == prevPart[4][j]:
                            scoresList = score[1]
                    if scoresList[preChosen.count(j) + 1] < bestScore:
                        bestScore = scoresList[postChosen.count(j) + 1]
                        bestLocate = 0
                        preHeld = j
                        preSelect = preIndex
                preSum -= abs(finalPre[-1 * (x)][j])

        for j in range(0, len(part[1]) - 1, 1): # for each note in the current part
            if finalPost[-1 * (x + 1)][j] != 0: # If the post movement allow movement
                postIndex = j
                specialMoves += abs(finalPost[-1 * (x + 1)][j])
            if (postSum + specialMoves) > 0: # If these is a possible move at current key in current part
                scoresList = []
                for score in noteScores: # Find the current note type and assign cost to scoreList
                    if score[0] == part[4][j]:
                        scoresList = score[1]
                if scoresList[postChosen.count(j) + 1] <= bestScore: # Determine if the current note has a better score for moving
                    bestScore = scoresList[postChosen.count(j) + 1]
                    bestLocate = 1
                    postHeld = j
                    postSelect = postIndex

        scoresList = []
        for score in noteScores:
            if score[0] == part[4][-1]:
                scoresList = score[1]
        if scoresList[lastChosen + 1] <= bestScore:
            bestScore = scoresList[lastChosen + 1]
            bestLocate = 2

        if bestLocate == -1:
            sys.exit("The music piece in not playable")

        if bestLocate == 0:
            preChosen.append(preHeld)
            if finalPre[-1 * (x)][preSelect] > 0:
                finalPre[-1 * (x)][preSelect] - 1
            elif finalPre[-1 * (x)][preSelect] < 0:
                finalPre[-1 * (x)][preSelect] + 1
            preSum - 1
        if bestLocate == 2:
            lastChosen += 1

        if bestLocate == 1:
            postChosen.append(postHeld)
            if postSelect != -1:
                if finalPost[-1 * (x + 1)][postSelect] > 0:
                    finalPost[-1 * (x + 1)][postSelect] - 1
                elif finalPost[-1 * (x + 1)][postSelect] < 0:
                    finalPost[-1 * (x + 1)][postSelect] + 1
            else:
                postSum - 1

    moveSet.append([lastChosen, postChosen, preChosen])

    prevPart = part

moveSet.reverse()

locations = []

currentValue = compare[0][0]


# TODO What does this do?

for x, part in enumerate(playSet):
    if len(playSet) == 1:
        locations = [playSet[0][0][-1]] * len(playSet[0][1])
        break
    for i, loc in enumerate(part[1]):
        locations.append(currentValue)
        if not (len(playSet) == (x + 1)):
            for j, movePart in enumerate(moveSet[x][1]):
                if movePart == i:
                    if sum(move[x]) > 0:
                        currentValue += 1
                    else:
                        currentValue -= 1
            if len(part[1]) == (i + 1):
                if sum(move[x]) > 0:
                    currentValue += moveSet[x][0]
                else:
                    currentValue -= moveSet[x][0]

playDurations = []

playLongevity = []

playNotes = []

playForce = []

movePosition = []

moveDuration = []

moveLongevity = []


durationSum = 0


# TODO This adds a force value for each note.

for part in locations:
    playForce.append(10)

# TODO What does this do? I think this finds how long each note should be held for. .i.e longevity

for x, part in enumerate(locations):
    if x == 0:
        playDurations.append(prePlay)
        noteTime = round(noteDuration / allValues[x])
        prevPart = part
        moveDuration.append(preMove)
        moveLongevity.append(
            math.ceil(travel_time(part * keyWidth, maxAccel, maxSpeed))
        )
        movePosition.append((part - beginningOffset) * keyWidth)
        durationSum += prePlay - preMove
        continue
    movement = abs(part - prevPart)
    timeUsed = travel_time(movement * keyWidth, maxAccel, maxSpeed)

    playLongevity.append(math.floor(noteTime - timeUsed - actuationTime))

    if movement != 0:
        durationSum += playLongevity[-1]
        movePosition.append((part - beginningOffset) * keyWidth)
        moveDuration.append(durationSum)
        moveLongevity.append(math.ceil(timeUsed))
        durationSum = 0
        durationSum += moveLongevity[-1] + actuationTime
    else:
        durationSum += noteTime

    playDurations.append(noteTime)

    noteTime = round(noteDuration / allValues[x])
    prevPart = part

playLongevity.append(math.floor(noteTime - timeUsed - actuationTime))

indexSole = []

binarySole = []


# TODO Create the output for which finger is playing which solenoid

for x, part in enumerate(locations):
    if (handedness == 0) & (sharp[x] == 1):
        change = 8
    else:
        change = 0

    indexSole.append(notes[values[x][1]].index(part))

    # playNotes.append(1 << (indexSole[x] + change))

    # playNotes.append(bin(binarySole[x])[2:].zfill(8))

    if rest[x] == 1:
        indexSole[x] = -1

    playNotes.append([base17[indexSole[x] + 1 + change], "0", "0", "0", "0"])


# TODO Generate Output File

output = str(("results.pcode"))

pcode = []
with open(output, "w") as f:
    f.write("s\n")

    for x, part in enumerate(playDurations):
        pcode.append("d")
        pcode.append("s" + str(handedness))
        pcode.append("n" + "".join(playNotes[x]))
        # pcode.append('n' + str(playNotes[x]))
        pcode.append("f" + str(playForce[x]))
        pcode.append("t" + str(playDurations[x]))
        pcode.append("l" + str(playLongevity[x]))

        toWrite = " ".join(pcode)

        toWrite = toWrite + "\n"

        f.write(toWrite)

        toWrite = ""
        pcode = []

    for x, part in enumerate(movePosition):
        pcode.append("h")
        pcode.append("s" + "0")
        pcode.append("p" + str(int(movePosition[x])))
        pcode.append("t" + str(moveDuration[x]))
        pcode.append("l" + str(moveLongevity[x]))

        toWrite = " ".join(pcode)

        toWrite = toWrite + "\n"

        f.write(toWrite)

        toWrite = ""
        pcode = []

    f.write("e")
# f.close()

print(f"p-code File Exported: {output}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True, help="input file: music.txt")
    ap.add_argument("-o", "--output", required=True, help="output file: results.pcode")
    args = ap.parse_args()

    music_path = Path(args.i)
    results_path = Path(args.o)
