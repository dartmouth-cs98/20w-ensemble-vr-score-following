from enum import Enum
from abc import abstractmethod
import pretty_midi
from math import floor

from src.music.Note import Note, Pitch, Duration


class ScoreFactory():
    @staticmethod
    def get_score(title):
        if title == Pieces.Twinkle:
            return TwinkleTwinkleScore()
        elif title == Pieces.Pachabels:
            return PachabelScore()


class Pieces(Enum):
    Twinkle = "Twinkle Twinkle Little Star"
    Pachabels = "Pachabels Canon"


class Score():
    def __init__(self):
        self.subdivided_notes = None
        self.tempo = None
        self.title = ""
        self.accompaniment = None
        self.sub_beat = Duration.Quarter

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
        return floor(event/4 - 0.25) + 1

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
        self.sub_beat = Duration.Eighth

    def set_notes(self):
        self.subdivided_notes = [Note(Pitch.REST, Duration.Eighth),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration.Eighth),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration.Eighth),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration.Eighth),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration.Eighth),
                                 Note(Pitch.E, Duration.Eighth),
                                 Note(Pitch.E, Duration.Eighth),
                                 Note(Pitch.E, Duration.Eighth),
                                 Note(Pitch.E, Duration.Eighth),
                                 Note(Pitch.D, Duration.Eighth),
                                 Note(Pitch.D, Duration.Eighth),
                                 Note(Pitch.D, Duration.Eighth),
                                 Note(Pitch.D, Duration.Eighth),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration.Eighth),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration.Eighth),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration.Eighth),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration.Eighth),
                                 Note(Pitch.B, Duration.Eighth),
                                 Note(Pitch.B, Duration.Eighth),
                                 Note(Pitch.B, Duration.Eighth),
                                 Note(Pitch.B, Duration.Eighth),
                                 Note(Pitch.A, Duration.Eighth),
                                 Note(Pitch.A, Duration.Eighth),
                                 Note(Pitch.A, Duration.Eighth),
                                 Note(Pitch.A, Duration.Eighth),
                                 Note(Pitch.B, Duration.Eighth),
                                 Note(Pitch.B, Duration.Eighth),
                                 Note(Pitch.B, Duration.Eighth),
                                 Note(Pitch.B, Duration.Eighth),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration.Eighth),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration.Eighth),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration.Eighth),
                                 Note(Pitch.C_SHARP_D_FLAT, Duration.Eighth)]
        self.N = len(self.subdivided_notes)

    def set_accompaniment(self):
        accompaniment = ['', 'D3', 'A3', 'D4', 'F#4', 'A2', 'E3', 'A3', 'C#4',
                              'B2', 'F#4', 'B3', 'D4', 'F#2', 'C#3', 'F#3', 'A3',
                              'G2', 'D3', 'G3', 'B3', 'D2', 'A2', 'D3', 'F#3',
                              'G2', 'D3', 'G3', 'B3', 'A2', 'E3', 'A3', 'C#4']
        self.accompaniment = [pretty_midi.note_name_to_number(note) if note != ''  else '' for note in accompaniment]

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
        self.subdivided_notes = [Note(Pitch.REST, Duration.Quarter),
                                 Note(Pitch.D, Duration.Quarter),
                                 Note(Pitch.D, Duration.Quarter),
                                 Note(Pitch.A, Duration.Quarter),
                                 Note(Pitch.A, Duration.Quarter),
                                 Note(Pitch.B, Duration.Quarter),
                                 Note(Pitch.B, Duration.Quarter),
                                 Note(Pitch.A, Duration.Quarter),  # Half
                                 Note(Pitch.A, Duration.Quarter),
                                 Note(Pitch.G, Duration.Quarter),
                                 Note(Pitch.G, Duration.Quarter),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration.Quarter),
                                 Note(Pitch.F_SHARP_G_FLAT, Duration.Quarter),
                                 Note(Pitch.E, Duration.Quarter),
                                 Note(Pitch.E, Duration.Quarter),
                                 Note(Pitch.D, Duration.Quarter),  # Half
                                 Note(Pitch.D, Duration.Quarter)]
        self.N = len(self.subdivided_notes)

    def set_tempo(self):
        self.tempo = 60

    def set_accompaniment(self):
        accompaniment = ['','A3', 'A3', 'F#4', 'F#4', 'G4', 'G4', 'F#4', 'F#4', 'E4', 'E4', 'D4', 'D4', 'A3', 'C#4', 'D4', 'D4']
        self.accompaniment = [pretty_midi.note_name_to_number(note) if note != ''  else '' for note in accompaniment]

    def get_accompaniment(self, event_num):
        return self.accompaniment[event_num]
