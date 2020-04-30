import sys

sys.path.append('../../')
from enum import Enum
from abc import abstractmethod
import pretty_midi
from math import floor
from src.interface.midi import MidiClient

from src.music.note import Note, Pitch, Duration


class ScoreBuilder():

    def __init__(self, filename, sub_beat):
        self.reset()
        self.midi_client = MidiClient()
        self.midi_client.load_file(filename)
        self.sub_beat = sub_beat
        self.parts = [
            self.midi_client.parse_track(i, is_solo=False) if i != 0 else self.midi_client.parse_track(i)
            for i in range(len(self.midi_client.midi_file.tracks) - 2)
        ]
        self.subdivided_parts = [self._subdivide_track(part, sub_beat) for part in self.parts]
        self._ensure_length()
        self.add_solo()
        self.add_accompaniment()
        self.create_subdivision_mapping(self.parts[0])

    def _ensure_length(self):
        """
        Pad the ends of parts if there is a rest at the very end to make sure all subdivided parts have the same
        number of events.
        :return:
        """
        part_lengths = [len(part) for part in self.subdivided_parts]
        max_length = max(part_lengths)
        for i, length in enumerate(part_lengths):
            if length != max_length:
                self.subdivided_parts[i].extend([Note(Pitch.REST, self.sub_beat)] * (max_length - length))

    def create_subdivision_mapping(self, notes):
        """
        Returns mapping of model-returned index i.e. the subdivided index to the actual index of the note.
        :param notes:
        :return:
        """
        subdiv_to_true_index = {}

        subdiv_index = 0
        for i, note in enumerate(notes):
            num_subdivisions = note.duration / self.sub_beat.value
            for j in range(int(num_subdivisions)):
                subdiv_to_true_index[subdiv_index] = i
                subdiv_index += 1
        self.product.true_note_mapping = subdiv_to_true_index

    def add_solo(self):
        self.product.notes = self.parts[0]
        self.product.subdivided_notes = self.subdivided_parts[0]
        self.product.N = len(self.product.subdivided_notes)

    def add_accompaniment(self):
        accompaniment = []
        parts = self.subdivided_parts[1:]

        for i in range(len(parts[0])):
            notes_at_event = {parts[j][i] for j in range(len(parts))}
            accompaniment.append(notes_at_event)

        self.product.accompaniment = accompaniment

    def _subdivide_track(self, notes, sub_beat):
        subdivided_track = []
        for note in notes:
            num_subdivisions = note.duration / sub_beat.value
            subdivided_note = [Note(note.pitch, sub_beat)] * int(num_subdivisions)
            subdivided_note[0].is_note_start = True
            subdivided_note[len(subdivided_note) - 1].is_note_end = True

            subdivided_track.extend(subdivided_note)
        return subdivided_track

    def reset(self):
        self.product = Score()

    def build(self):
        product = self.product
        self.reset()
        return product


class ScoreFactory():
    @staticmethod
    def get_score(title):
        if title == Pieces.Twinkle:
            return TwinkleTwinkleScore()
        elif title == Pieces.Pachabels:
            return PachabelScore()
        else:
            return ScoreBuilder('../../res/midi/Pachabels/Pachelbels_Canon_in_D_String_Quartet.mid',
                                Duration(0.25)).build()


class Pieces(Enum):
    Twinkle = "Twinkle Twinkle Little Star"
    Pachabels = "Pachabels Canon"


class Score():
    def __init__(self):
        self.subdivided_notes = None
        self.notes = None
        self.tempo = None
        self.title = ""
        self.accompaniment = None
        self.sub_beat = Duration(1)
        self.true_note_mapping = None
        self.N = 0

    @abstractmethod
    def set_notes(self):
        pass

    @abstractmethod
    def set_tempo(self):
        pass

    @abstractmethod
    def set_accompaniment(self):
        pass

    def get_true_note_event(self, event):
        return self.true_note_mapping[event] + 1
        # return floor(event / 4 - 0.25) + 1

    def get_accompaniment(self, event_num):
        return self.accompaniment[event_num]


class PachabelScore(Score):
    def __init__(self):
        super().__init__()
        self.title = "Pachabel's Canon in D"
        self.N = 0
        self.set_notes()
        self.set_tempo()
        self.set_accompaniment()
        self.sub_beat = Duration(0.5)

    def set_notes(self):
        self.subdivided_notes = [Note(Pitch.D, Duration(0.5)),  # Bullshit Note
                                 Note(Pitch.REST, Duration(0.5)),
                                 Note(Pitch.REST, Duration(0.5)),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration(0.5)),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration(0.5)),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration(0.5)),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration(0.5)),
                                 Note(Pitch.E, Duration(0.5)),
                                 Note(Pitch.E, Duration(0.5)),
                                 Note(Pitch.E, Duration(0.5)),
                                 Note(Pitch.E, Duration(0.5)),
                                 Note(Pitch.D, Duration(0.5)),
                                 Note(Pitch.D, Duration(0.5)),
                                 Note(Pitch.D, Duration(0.5)),
                                 Note(Pitch.D, Duration(0.5)),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration(0.5)),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration(0.5)),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration(0.5)),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration(0.5)),
                                 Note(Pitch.B, Duration(0.5)),
                                 Note(Pitch.B, Duration(0.5)),
                                 Note(Pitch.B, Duration(0.5)),
                                 Note(Pitch.B, Duration(0.5)),
                                 Note(Pitch.A, Duration(0.5)),
                                 Note(Pitch.A, Duration(0.5)),
                                 Note(Pitch.A, Duration(0.5)),
                                 Note(Pitch.A, Duration(0.5)),
                                 Note(Pitch.B, Duration(0.5)),
                                 Note(Pitch.B, Duration(0.5)),
                                 Note(Pitch.B, Duration(0.5)),
                                 Note(Pitch.B, Duration(0.5)),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration(0.5)),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration(0.5)),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration(0.5)),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration(0.5))]
        self.N = len(self.subdivided_notes)

    def set_accompaniment(self):
        accompaniment = ['', 'A3', 'C#4c', 'D3', 'A3', 'D4', 'F#4', 'A2', 'E3', 'A3', 'C#4',
                         'B2', 'F#4', 'B3', 'D4', 'F#2', 'C#3', 'F#3', 'A3',
                         'G2', 'D3', 'G3', 'B3', 'D2', 'A2', 'D3', 'F#3',
                         'G2', 'D3', 'G3', 'B3', 'A2', 'E3', 'A3', 'C#4']
        self.accompaniment = [pretty_midi.note_name_to_number(note) if note != '' else '' for note in accompaniment]

    def set_tempo(self):
        self.tempo = 60


class TwinkleTwinkleScore(Score):

    def __init__(self):
        super().__init__()
        self.title = "Twinkle Twinkle Little Star"
        self.N = 0
        self.set_notes()
        self.set_tempo()
        self.set_accompaniment()

    def set_notes(self):
        # self.notes = [2, 2, 9, 9, 11, 11, 9, 7, 7, 6, 6, 4, 4, 2]
        self.subdivided_notes = [
            Note(Pitch.REST, Duration(1.0)),
            Note(Pitch.D, Duration(1.0)),
            Note(Pitch.D, Duration(1.0)),
            Note(Pitch.A, Duration(1.0)),
            Note(Pitch.A, Duration(1.0)),
            Note(Pitch.B, Duration(1.0)),
            Note(Pitch.B, Duration(1.0)),
            Note(Pitch.A, Duration(1.0)),  # Half
            Note(Pitch.A, Duration(1.0)),
            Note(Pitch.G, Duration(1.0)),
            Note(Pitch.G, Duration(1.0)),
            Note(Pitch.F_SHARP_G_FLAT, Duration(1.0)),
            Note(Pitch.F_SHARP_G_FLAT, Duration(1.0)),
            Note(Pitch.E, Duration(1.0)),
            Note(Pitch.E, Duration(1.0)),
            Note(Pitch.D, Duration(1.0)),  # Half
            Note(Pitch.D, Duration(1.0))]
        self.N = len(self.subdivided_notes)

    def set_tempo(self):
        self.tempo = 60

    def set_accompaniment(self):
        accompaniment = ['', 'A3', 'A3', 'F#4', 'F#4', 'G4', 'G4', 'F#4', 'F#4', 'E4', 'E4', 'D4', 'D4', 'A3', 'C#4',
                         'D4', 'D4']
        self.accompaniment = [pretty_midi.note_name_to_number(note) if note != '' else '' for note in accompaniment]

    def get_accompaniment(self, event_num):
        return self.accompaniment[event_num]
