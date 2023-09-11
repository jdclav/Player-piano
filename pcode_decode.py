base17 = (
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
)


def sorted_commandsList(path: str):
    """Take a file path for a pcode file and returns a list of the commands in time
    sorted order"""

    f = open(path, "rt")

    commands = f.read().split("\n")

    commandsList = []

    for com in commands:
        commandsList.append(com.split(" "))

    dCommandsList = []

    hCommandsList = []

    for com in commandsList:
        if com[0] == "d":
            dCommandsList.append(com)

        elif com[0] == "h":
            hCommandsList.append(com)

    dPlayTime = 0

    for com in dCommandsList:
        com[1] = int(com[1][1:])
        com[2] = com[2][1:]
        com[3] = int(com[3][1:])
        com[4] = int(com[4][1:])
        com[5] = int(com[5][1:])

        dPlayTime = dPlayTime + com[4]

        com[4] = dPlayTime

        playKeys = []

        for digit in com[2]:
            if digit != "0":
                playKeys.append(base17.index(digit))

        com[2] = playKeys

    hPlayTime = 0

    for com in hCommandsList:
        com[1] = int(com[1][1:])
        com[2] = int(com[2][1:])
        com[3] = int(com[3][1:])
        com[4] = int(com[4][1:])

        hPlayTime = hPlayTime + com[3]

        com[3] = hPlayTime

    # commandsList = hCommandsList + dCommandsList

    # commandsList.sort(key=lambda x: x[3] if x[0] == "h" else x[4])

    hCommandsList.sort(key=lambda x: x[3])

    dCommandsList.sort(key=lambda x: x[4])

    commandsList = [hCommandsList, dCommandsList]

    return commandsList
