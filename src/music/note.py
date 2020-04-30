from enum import Enum

class Note:
    def __init__(self, pitch, duration, is_note_start=False, is_note_end=False):
        self.pitch = pitch
        self.duration = duration
        self.is_note_start = is_note_start
        self.is_note_end = is_note_end

    def __str__(self):
        return "<{0}, {1}>".format(self.pitch, self.duration)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def note_name_to_pitch_enum(note_name):
        map = {
            "C": Pitch.C,
            "C#": Pitch.C_SHARP_D_FLAT,
            "D": Pitch.D,
            "D#": Pitch.D_SHARP_E_FLAT,
            "E": Pitch.E,
            "F": Pitch.F,
            "F#": Pitch.F_SHARP_G_FLAT,
            "G": Pitch.G,
            "G#": Pitch.G_SHARP_A_FLAT,
            "A": Pitch.A,
            "A#": Pitch.A_SHARP_B_FLAT,
            "B": Pitch.B
        }
        return map[note_name] if not note_name[-1].isdigit() else map[note_name[:-1]]

class Pitch(Enum):
    REST = -1
    C = 0
    C_SHARP_D_FLAT = 1
    D = 2
    D_SHARP_E_FLAT = 3
    E = 4
    F = 5
    F_SHARP_G_FLAT = 6
    G = 7
    G_SHARP_A_FLAT = 8
    A = 9
    A_SHARP_B_FLAT = 10
    B = 11


class Duration:
    # Sixteenth = 0.25
    # Eighth = 0.5
    # Quarter = 1
    # Dotted_Quarter = 1.5
    # Half = 2
    # Dotted_Half = 3
    # Whole = 4

    def __init__(self, duration):
        self.value = float(duration)
