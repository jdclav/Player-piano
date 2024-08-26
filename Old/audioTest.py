import numpy as np
import simpleaudio as sa

EMPTY_SOUND = -1

class TBD:
    def __init__(self, start_time: int, frequency: int, duration: int, sample_rate: int) -> None:

        self.frequency = frequency
        self.duration = duration

        samples_per_ms = int(sample_rate / 1000)

        samples = np.linspace(0, duration, duration * samples_per_ms, False)

        self.waveform = np.sin(frequency * (samples  / 1000) * 2 * np.pi)

        self.normalized *= 32767 / np.max(np.abs(self.waveform))

        self.start_time = start_time

class Note:
    def __init__(self, start_time: int, midi_note: int, duration: int, force: int) -> None:
        self.start_time = start_time
        self.midi_note = midi_note
        self.duration = duration

class NoteList:
    def __init__(self):
        self.note_list = []

    def find_note(self, midi_note: int) -> Note:
        if(self.note_list == []):
            return (Note(previous_time, EMPTY_SOUND, current_time - previous_time, 0))



def midi_to_freq(midi_note: int) -> float:
    A4_freq = 440
    A4_midi = 69

    freq = A4_freq * 2 ** ((midi_note - A4_midi) / 12)

    return freq


if __name__ == "__main__":

    for x in range(0, 129):
        print(midi_to_freq(x))


    """
    # Note frequencies
    first_freq = 440
    next_freq = first_freq * 2 ** (7 / 12)
    
    # samples per second
    smpl_rate = 48000
    
    # Generate array(timesteps) with 
    # seconds*sample_rate steps, 
    # ranging between 0 and seconds

    first_note = Note(first_freq, 500, smpl_rate)
    next_note = Note(next_freq, 500, smpl_rate)

    
    # merging the notes
    tape = np.hstack((first_note.waveform,next_note.waveform))
    #tape = np.add(first_note.waveform,next_note.waveform)
    # normalizing to 16-bit range 
    # after concatenating the note notes
    

    tape *= 0.2 
    
    # Converting to 16-bit data
    tape = tape.astype(np.int16)
    
    # Start audio
    play = sa.play_buffer(tape, 1, 2, smpl_rate)
    
    # Wait for audio playback to finish before exiting
    play.wait_done()
    play.stop()
    """