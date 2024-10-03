BASE18 = (
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
    def __init__(self, command_str: str) -> None:
        self.command_str = command_str

        self.command_type = command_str[0]

        if self.command_type == "h":
            self.process_move_command()
        if self.command_type == "d":
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

        temp_solenoid_list: list[int] = []

        for solenoid in temp_solenoid_locations:
            if solenoid != "0":
                temp_solenoid_list.append(BASE18.index(solenoid))

        self.solenoid_locations = temp_solenoid_list

    def __str__(self) -> str:
        return self.command_str


class CommandList:
    def __init__(self, path: str) -> None:
        with open(path, "rt") as f:
            self.file_commands = f.read().split("\n")

        self.play_commands: list[Command] = []
        self.move_commands: list[Command] = []
        self.in_order_commands: list[Command] = []

        self.sort_commands()
        self.convert_duration()

    def sort_commands(self) -> None:
        for com in self.file_commands:
            processed_command = Command(com)

            if processed_command.command_type == "d":
                self.play_commands.append(processed_command)

            elif processed_command.command_type == "h":
                self.move_commands.append(processed_command)

    def convert_duration(self) -> None:
        play_time = 0
        move_time = 0

        for com in self.play_commands:
            play_time += com.duration
            com.duration = play_time

        for com in self.move_commands:
            move_time += com.duration
            com.duration = move_time

        self.move_commands.sort(key=lambda x: x.duration)
        self.play_commands.sort(key=lambda x: x.duration)
        self.in_order_commands = self.move_commands + self.play_commands
        self.in_order_commands.sort(key=lambda x: x.duration)
