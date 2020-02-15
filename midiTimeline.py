import mido
import numpy as np


class TimeLine:
    def __init__(self, midi_file):
        self.time_line = {}
        self.midi_file = midi_file

    def gen_time_line(self):
        """
        generate a timeline of the midi score to function as ground truth for training model
        constructs it based on which notes should be playing at the current time
        """
        curr_time = 0
        on_notes = []
        for i in range(1, len(self.midi_file.tracks)):
            for message in self.midi_file.tracks[i]:
                curr_time += message.time
                if(message.type == 'note_on'):
                    on_notes.append(message.note)
                    self.time_line[curr_time] = on_notes.copy()
                elif(message.type == 'note_off'):
                    on_notes.remove(message.note)
                    self.time_line[curr_time] = on_notes.copy()

    def get_time_line(self):
        return self.time_line

    def get_midi_file(self):
        return self.midi_file

    def play_back(self, time):
        self.time_line[time]

