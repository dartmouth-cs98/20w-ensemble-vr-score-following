from enum import Enum


class Note:

    def __init__(self, pitch, duration):
        self.pitch = pitch
        self.duration = duration


class Pitch(Enum):
    C = 0,
    C_SHARP_D_FLAT = 1,
    D = 2,
    D_SHARP_E_FLAT = 3,
    E = 4,
    F = 5,
    F_SHARP_G_FLAT = 6,
    G = 7,
    G_SHARP_A_FLAT = 8,
    A = 9,
    A_SHARP_B_FLAT = 10,
    B = 11,


class Duration(Enum):
    Sixteenth = 0.25
    Eighth = 0.5
    Quarter = 1
    Half = 2
    Dotted_Half = 3
    Whole = 4
