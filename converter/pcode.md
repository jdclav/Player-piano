### PCODE command definitions

## Start Command

# Description

This command should be at the top of every file. This marks the beginning of the piece as well as retaining various values assumed during the generation of the pcode.

# Breakdown

- s : The character signifying the command type is "Start".
- a : The default acceleration for the file in mm/s^2 as an integer.
- v : The default max velocity for the file in mm/s as an integer.
- w : The defined key width for the white piano keys in mm as a decimal.
- d : The defined solenoid retract time in microseconds as an integer.
- p : The defined pause from time zero to the first note of the piece in microseconds as an integer.

## End Command

# Description

This denotes the end of the piece. Pcode could exist after this if being used by a repeat command.

# Breakdown

- e : This character signifying the command type is "End".

## Deploy Command

# Description

This command signals that solenoids will be deployed with the intent to play keys on the keyboard.

# Breakdown

- d : The character signifying the command type is "Start".