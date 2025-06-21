### PCODE command definitions

## Start Command

# Description

This command should be at the top of every file. This marks the beginning of the piece as well as retaining various values assumed during the generation of the pcode.

# Breakdown

- s : The character signifying the command type is "Start".
- a : The default acceleration for the file in mm/s^2 as a 32 bit integer.
- v : The default max velocity for the file in mm/s as a 32 bit integer.
- w : The defined key width for the white piano keys in mm as a decimal.
- d : The defined solenoid retract time in microseconds as a 32 bit integer.
- p : The defined pause from time zero to the first note of the piece in microseconds as a 32 bit integer.

## End Command

# Description

This denotes the end of the piece. Pcode could exist after this if being used by a repeat command.

# Breakdown

- e : This character signifying the command type is "End".

## Deploy Command

# Description

This command signals that solenoids will be deployed with the intent to play keys on the keyboard.

# Breakdown

- d : The character signifying the command type is "Deploy".
- h : The hand this command in intended for as either a capital L or R.
- f : The fingering for the deploy. This will be a five digit base 18 number. The digit position represents the "finger" that should play that note. The value at the digit represents which solenoid should be deployed for that "finger". "H" means no solenoid should be deployed for that finger.
- v : The velocity, or volume, the deploy should produce as an integer between 0 and 127. This should behave identical to MIDI velocity.
- t : The absolute time from time zero this command should take place in microseconds as a 64 bit integer.
- l : The longevity of the command. This will be how long the solenoids should remain deployed from the start of the command in microseconds as a 64 bit integer.

## Move Command

# Description

This command signals that a hand will be moved to a position.

# Breakdown

- m : The character signifying the command type is "Move".
- h : The hand this command in intended for as either a capital L or R.
- t : The absolute time from time zero this command should take place in microseconds as a 64 bit integer.
- l : The longevity of the command. This will be how long a move should take in totality from the start of the command to the end of motion in microseconds as a 64 bit integer.

## Pedal Command

# Description

This command signals that a pedal will be depressed.

# Breakdown

TBD

## Repeat Command

# Description

This command points to a command and jumps to that command. It also specifies how many times to repeat or if it should wait for a external stop trigger.

# Breakdown

TBD