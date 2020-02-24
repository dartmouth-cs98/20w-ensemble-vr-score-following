import mido
from mido import Message
import time


class TimeLine:
    def __init__(self, midi_file):
        self.time_line = {}
        self.midi_file = midi_file
        self.playing_notes = []
        self.setup = []

    def gen_time_line(self):
        """
        generate a timeline of the midi score to function as ground truth for training model
        constructs it based on which notes should be playing at the current time
        """
        setup_unfinished = True
        curr_time = 0
        on_notes = []
        for i in range(len(self.midi_file.tracks)):
            for message in self.midi_file.tracks[i]:
                curr_time += message.time
                if message.type == 'note_on':
                    setup_unfinished = False
                    on_notes.append(message.note)
                    self.time_line[curr_time] = on_notes.copy()
                elif message.type == 'note_off':
                    on_notes.remove(message.note)
                    self.time_line[curr_time] = on_notes.copy()
                elif setup_unfinished:
                    self.setup.append(message)

    def get_time_line(self):
        return self.time_line

    def get_midi_file(self):
        return self.midi_file

    def play_back(self, key):
        """
        sends the message at time indicated by key
        """
        t0 = time.time()
        port = mido.open_output('New Port', virtual=True)
        for message in self.midi_file.play():
            port.send(message)

        """for message in self.setup:
            print(message)
            port.send(message)
        if time.time() - t0 in self.time_line.keys():
            for note in self.playing_notes:
                if note not in self.time_line[time.time() - t0]:
                    message = Message('note_off', note=note, velocity=100, time=0)
                    port.send(message)
                    self.playing_notes.remove(note)
            for note in self.time_line[time.time() - t0]:
                if note not in self.playing_notes:
                    message = Message('note_on', note=note, velocity=100, time=0)
                    port.send(message)
                    self.playing_notes.append(note)
"""
