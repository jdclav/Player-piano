import numpy as np


EMPTY_SOUND = -1
PENDING_DURATION = 0

"""class TBD:
    def __init__(self, start_time: int, frequency: int, duration: int, sample_rate: int) -> None:

        self.frequency = frequency
        self.duration = duration

        samples_per_ms = int(sample_rate / 1000)

        samples = np.linspace(0, duration, duration * samples_per_ms, False)

        self.waveform = np.sin(frequency * (samples  / 1000) * 2 * np.pi)

        self.normalized *= 32767 / np.max(np.abs(self.waveform))

        self.start_time = start_time"""

class Note:
    def __init__(self, start_time: int, midi_note: int, duration: int, velocity: int) -> None:
        self.start_time = start_time
        self.midi_note = midi_note
        self.duration = duration
        self.velocity = velocity

    def set_duration(self, duration: int) -> None:
        self.duration = duration

    def set_start_sample(self, us_per_tick: float, sample_rate: int):
        samples_per_ms = int(sample_rate / 1000)
        self.start_sample = int(samples_per_ms * self.start_time * us_per_tick / 1000)

    def note_waveform(self, us_per_tick: float, sample_rate: int) -> None:
        frequency = midi_to_freq(self.midi_note)
        duration_in_s = (self.duration * us_per_tick / 1000000.0)

        samples = np.linspace(0, duration_in_s, int(duration_in_s * sample_rate), False)

        self.waveform = np.sin(frequency * samples * 2 * np.pi)
    


class NoteList:
    def __init__(self):
        self.note_list: list[Note] = []
        self.pending_list: list[Note] = []

    def find_note(self, midi_note: int, current_time: int, previous_time: int, velocity: int) -> None:

        duration = current_time - previous_time 

        if(self.pending_list == [] and (duration > 0)):
            self.note_list.append(Note(previous_time, EMPTY_SOUND, duration, 0))

        for item in self.pending_list:
            if item.midi_note == midi_note:
                new_note = item
                self.pending_list.remove(item)
                duration = current_time - item.start_time
                item.set_duration(duration)
                self.note_list.append(new_note)
                return
        else:
            self.pending_list.append(Note(current_time, midi_note, PENDING_DURATION, velocity))

    def full_waveform(self, total_duration: int, us_per_tick: float, sample_rate: int) -> None:
        total_duration_in_s = (total_duration * us_per_tick / 1000000.0)
        full_samples = np.linspace(0, total_duration_in_s, int(total_duration_in_s * sample_rate), False)

        for item in self.note_list:

            item.note_waveform(us_per_tick, sample_rate)

            item.set_start_sample(us_per_tick, sample_rate)

            sample_len = len(item.waveform) + item.start_sample

            full_samples[item.start_sample:sample_len] += item.waveform

        full_samples *= 32767 / np.max(np.abs(full_samples))

        full_samples *= 0.2 
    
            # Converting to 16-bit data
        self.waveform = full_samples.astype(np.int16)
            

    def print_note_list(self):
        for note in self.note_list:
            print("Note: " + str(note.midi_note) + " Start Time: " + str(note.start_time) + " Duration: " + str(note.duration) + " Velocity: " + str(note.velocity))



        



def midi_to_freq(midi_note: int) -> float:
    A4_freq = 440
    A4_midi = 69

    if(midi_note == -1):
        return 0

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