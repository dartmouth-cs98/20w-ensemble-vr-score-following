from enum import Enum
from abc import abstractmethod

from src.model.Note import Note, Pitch, Duration


class ScoreFactory():
    @staticmethod
    def get_score(title):
        if title == Pieces.Twinkle:
            return TwinkleTwinkleScore()


class Pieces(Enum):
    Twinkle = "Twinkle Twinkle Little Star"
    Pachabels = "Pachabels Canon"


class Score():
    def __init__(self):
        self.notes = None
        self.tempo = None
        self.title = ""

    @abstractmethod
    def set_notes(self):
        pass

    @abstractmethod
    def set_tempo(self):
        pass


class TwinkleTwinkleScore(Score):

    def __init__(self):
        super().__init__()
        self.title = "Twinkle Twinkle Little Star"
        self.N = 0
        self.set_notes()
        self.set_tempo()

    def set_notes(self):
        # self.notes = [2, 2, 9, 9, 11, 11, 9, 7, 7, 6, 6, 4, 4, 2]
        self.notes = [Note(Pitch.D, Duration.Quarter),
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
        self.N = len(self.notes)

    def set_tempo(self):
        self.tempo = 65
