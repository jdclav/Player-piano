import mido
import audioTest
import simpleaudio as sa
import os


SAMPLE_RATE = 48000

dir_path = os.path.dirname(os.path.realpath(__file__))

mid = mido.MidiFile(dir_path + "/underground.mid")

metaMessages: list[mido.Message] = mid.tracks[0].copy()
noteMessages: list[mido.Message] = mid.tracks[1].copy()
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
    if msg.type == "note_on":
        current_time += msg.time
        notes.find_note(msg.note, current_time, previous_time, msg.velocity)
        previous_time = current_time

    else:
        current_time += msg.time


notes.full_waveform(current_time, us_per_tick, SAMPLE_RATE)

# Start audio
play = sa.play_buffer(notes.waveform, 1, 2, SAMPLE_RATE)

# Wait for audio playback to finish before exiting
play.wait_done()
play.stop()
