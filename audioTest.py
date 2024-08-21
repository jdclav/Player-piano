import numpy as np
import simpleaudio as sa

class Note:
    def __init__(self, frequency: int, duration: int, sample_rate: int) -> None:

        self.frequency = frequency
        self.duration = duration

        duration_seconds = int(duration / 1000)

        samples = np.linspace(0, duration_seconds, duration_seconds * sample_rate, False)

        self.waveform = np.sin(frequency * samples * 2 * np.pi)


if __name__ == "__main__":
    # Note frequencies
    first_freq = 400 
    next_freq = first_freq * 2 ** (7 / 12)
    
    # samples per second
    smpl_rate = 48000
    
    # Generate array(timesteps) with 
    # seconds*sample_rate steps, 
    # ranging between 0 and seconds

    first_note = Note(first_freq, 1000, smpl_rate)
    next_note = Note(next_freq, 1000, smpl_rate)

    
    # merging the notes
    #tape = np.hstack((first_note.waveform,next_note.waveform))
    tape = np.add(first_note.waveform,next_note.waveform)
    # normalizing to 16-bit range 
    # after concatenating the note notes
    tape *= 32767 / np.max(np.abs(tape))

    tape *= 0.2
    
    # Converting to 16-bit data
    tape = tape.astype(np.int16)
    
    # Start audio
    play = sa.play_buffer(tape, 1, 2, smpl_rate)
    
    # Wait for audio playback to finish before exiting
    play.wait_done()
    play.stop()