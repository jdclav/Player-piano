from frame import PianoFrame, AudioFrame
from audioTest import NoteList
import simpleaudio as sa

SAMPLE_RATE = 48000

piano_frame = PianoFrame()

audio_frame = AudioFrame()

piano_frame.populate_hand(15)

piano_frame.actuate([0])

audio_frame.set_frame_time(0)

audio_frame.line_index_to_midi(piano_frame)

piano_frame.retract(100)

audio_frame.set_frame_duration(100)

us_per_tick = 1000
previous_time = 0
current_time = 0
notes = NoteList()


notes.find_note(audio_frame.midi_notes[0], 0, 0, 10)
notes.find_note(audio_frame.midi_notes[0], 1000, 0, 10)

notes.full_waveform(1000, us_per_tick, SAMPLE_RATE)

# Start audio
play = sa.play_buffer(notes.waveform, 1, 2, SAMPLE_RATE)

# Wait for audio playback to finish before exiting
play.wait_done()
play.stop()
