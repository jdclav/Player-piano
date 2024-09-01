from frame import PianoFrame, AudioFrame

piano_frame = PianoFrame()

audio_frame = AudioFrame()

piano_frame.populate_hand(15)

piano_frame.actuate([4, 13])

audio_frame.line_index_to_midi(piano_frame)

print(piano_frame)
