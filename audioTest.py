import numpy as np
import simpleaudio as sa
# Note frequencies
first_freq = 400 
nxt_freq = first_freq * 2 ** (7 / 12)
 
# samples per second
smpl_rate = 44100
# Note duration in seconds
seconds = 3 
 
# Generate array(timesteps) with 
# seconds*sample_rate steps, 
# ranging between 0 and seconds
arr = np.linspace(0, seconds, seconds * smpl_rate, False)
 
# Generate a 400Hz Sine wave
first_note = np.sin(first_freq * arr * 2 * np.pi)
nxt_note = np.sin(nxt_freq * arr * 2 * np.pi)
 
# merging the notes
tape = np.hstack((first_note,nxt_note))
 
# normalizing to 16-bit range 
# after concatenating the note notes
tape *= 32767 / np.max(np.abs(tape))
 
# Converting to 16-bit data
tape = tape.astype(np.int16)
 
# Start audio
play = sa.play_buffer(tape, 1, 2, smpl_rate)
 
# Wait for audio playback to finish before exiting
play.wait_done()
play.stop()