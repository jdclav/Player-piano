import mido

import musicalbeeps

player = musicalbeeps.Player()

mid = mido.MidiFile("underground.mid")

metaMessages = mid.tracks[0].copy()

noteMessages = mid.tracks[1].copy()

timeSignature = None

tempo = None

usPerTick = None

for msg in metaMessages:
    if msg.type == "time_signature":
        timeSignature = msg

    if msg.type == "set_tempo":
        tempo = msg.tempo

""" for msg in noteMessages:

    if msg.type=="note_on":
        print(msg)
 """
usPerTick = tempo / mid.ticks_per_beat

player.play_note("B", 0.2)

""" for msg in mid.play():
    if msg.type == "note_on":
        print(msg.note)
 """
