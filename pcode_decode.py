base18 = (
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
    "H",
)


START_COMMENT = 0
MOVE_COMMAND = 1
DEPLOY_COMMAND = 2
END_COMMAND = 3

class Command:
    def __init__ (self, command_str: str) -> None:
        self.command_str = command_str

        self.command_type = command_str[0]

        if(self.command_type == "h"):
            self.process_move_command()
        if(self.command_type == "d"):
            self.process_play_command()

    
    def process_move_command(self) -> None:

        split_command = self.command_str.split(" ")

        self.hand = int(split_command[1][1:])
        self.position = int(split_command[2][1:])
        self.duration = int(split_command[3][1:])
        self.longevity = int(split_command[4][1:])        
        
    def process_play_command(self) -> None:
        
        split_command = self.command_str.split(" ")

        self.hand = int(split_command[1][1:])
        self.force = int(split_command[3][1:])
        self.duration = int(split_command[4][1:])
        self.longevity = int(split_command[5][1:]) 

        temp_solenoid_locations = split_command[2][1:]
        
        temp_solenoid_list = []

        for solenoid in temp_solenoid_locations:
            if solenoid != "0":
                temp_solenoid_list.append(base18.index(solenoid))

        self.solenoid_locations = temp_solenoid_list



def sorted_commandsList(path: str):
    """Take a file path for a pcode file and returns a list of the commands in time
    sorted order"""

    f = open(path, "rt")

    commands = f.read().split("\n")

    commandsList = []


    dCommandsList: list[Command] = []

    hCommandsList: list[Command] = []

    for com in commands:

        processed_command = Command(com)

        if processed_command.command_type == "d":
            dCommandsList.append(processed_command)

        elif processed_command.command_type == "h":
            hCommandsList.append(processed_command)

    dPlayTime = 0

    """"""

    for com in dCommandsList:

        dPlayTime = dPlayTime + com.duration

        com.duration = dPlayTime

    """"""

    hPlayTime = 0

    for com in hCommandsList:

        hPlayTime = hPlayTime + com.duration

        com.duration = hPlayTime

    hCommandsList.sort(key=lambda x: x.duration)

    dCommandsList.sort(key=lambda x: x.duration)

    commandsList = [hCommandsList, dCommandsList]

    return commandsList

