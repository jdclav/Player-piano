import mido
import time
import audioTest
import numpy as np

SAMPLE_RATE = 48000


mid = mido.MidiFile("underground.mid")

metaMessages = mid.tracks[0].copy()

noteMessages = mid.tracks[1].copy()

timeSignature = None

tempo = None

usPerTick = None

notes = []

pending = []

for msg in metaMessages:
    if msg.type == "time_signature":
        timeSignature = msg

    if msg.type == "set_tempo":
        tempo = msg.tempo

usPerTick = tempo / mid.ticks_per_beat

current_note = 0

current_time = 0

previous_time = 0

notes = []

for msg in noteMessages:

    if msg.type=="note_on":

        #print(msg)
        
        """        
        print("Note: " + str(msg.note))
        print("Time: " + str(msg.time))
        print("Current Time: " + str(current_time))
        """

        current_time += msg.time

        

        elif(msg.note in pending):
            pending.remove(msg.note)
            current_note = msg.note
        else:
            pending.append(msg.note)
            continue



        

        
        
        



        
"""
current_duration = int(msg.time * usPerTick / 1000.0)

samples = np.linspace(0, current_duration, current_duration * int(SAMPLE_RATE / 1000), False)

"""





