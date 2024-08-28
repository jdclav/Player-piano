import mido
#import time
import audioTest
import numpy as np
import simpleaudio as sa


SAMPLE_RATE = 48000


mid = mido.MidiFile("underground.mid")

metaMessages = mid.tracks[0].copy()

noteMessages = mid.tracks[1].copy()

timeSignature = None


for msg in metaMessages:
    if msg.type == "time_signature":
        timeSignature = msg

    if msg.type == "set_tempo":
        tempo = msg.tempo

us_per_tick = tempo / mid.ticks_per_beat

previous_time = 0

current_time = 0

notes = audioTest.NoteList()

for msg in noteMessages:

    if msg.type=="note_on":

        current_time += msg.time

        notes.find_note(msg.note, current_time, previous_time, msg.velocity)

        previous_time = current_time
        
        """        
        print("Note: " + str(msg.note))
        print("Time: " + str(msg.time))
        print("Current Time: " + str(current_time))
        """
    else:
        current_time += msg.time




"""test_note = notes.note_list[1]

test_note.note_waveform(us_per_tick, SAMPLE_RATE)

test_waveform = test_note.waveform

test_waveform *= 32767 / np.max(np.abs(test_waveform))

test_waveform *= 0.2

test_waveform = test_waveform.astype(np.int16)

play = sa.play_buffer(test_waveform, 1, 2, SAMPLE_RATE)"""
    
notes.full_waveform(current_time, us_per_tick, SAMPLE_RATE)

    # Start audio
play = sa.play_buffer(notes.waveform, 1, 2, SAMPLE_RATE)

# Wait for audio playback to finish before exiting
play.wait_done()
play.stop()



"""        current_time += msg.time

        

        elif(msg.note in pending):
            pending.remove(msg.note)
            current_note = msg.note
        else:
            pending.append(msg.note)
            continue
"""

        
"""
current_duration = int(msg.time * usPerTick / 1000.0)

samples = np.linspace(0, current_duration, current_duration * int(SAMPLE_RATE / 1000), False)

"""