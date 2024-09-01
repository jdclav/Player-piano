from frame import PianoFrame, AudioFrame

piano_frame = PianoFrame()

audio_frame = AudioFrame()

piano_frame.populate_hand(15)

piano_frame.actuate([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])

audio_frame.line_index_to_midi(piano_frame)

print(piano_frame)

print(audio_frame.midi_notes)
