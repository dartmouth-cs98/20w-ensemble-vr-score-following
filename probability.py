from enum import Enum

import numpy as np
from scipy.stats import cauchy, expon


class PitchType(Enum):
    CHORD = "chord",
    SEMITONE = "semitone",
    WHOLETONE = "wholetone",
    OCTAVE = "octave",
    RESIDUAL = "residual"


class MusicalEvent:
    def __init__(self, prev_event, note_value, onset_time):
        self.pitches = []       # List of MIDI degrees
        self.residuals = prev_event.pitches
        self.note_value = note_value
        self.onset_time = onset_time

    def get_C_i_chord(self):
        return self.pitches

    def get_C_i_semitone(self):
        return set(note + 1 for note in self.pitches) + set(note - 1 for note in self.pitches)

    def get_C_i_wholetone(self):
        return set(note + 2 for note in self.pitches) + set(note - 2 for note in self.pitches)

    def get_C_i_octave(self):
        return set(note + 12 for note in self.pitches) + set(note - 12 for note in self.pitches)

    def get_C_i_residual(self):
        return self.residuals



def emission_matrix(size_i = 10, size_s = 100, size_p = 10, size_t = 10):
    """
    emission matrix of size K x N such that B_ij stores the probability
    of observing o_j from state s_i
    :return: numpy array of size K x N
    """
    emission_matrix = np.zeros((size_i, size_s, size_p, size_t))

    for i in range(size_i):
        for s in range(size_s):
            for p in range(size_p):
                for t in range(size_t):
                    emission_matrix[i][s][p][t] = pitch_probability() * onset_time_probability()


    return emission_matrix


def pitch_probability(musical_event: MusicalEvent):
    """
    :param musical_event: the current musical event
    :return: joint probability of all notes in musical event.
    """

    p_a = 0
    joint_prob = 1

    for pitch in musical_event.pitches:
        pitch_type = pitch[1]
        c_i_a = None

        if pitch_type is PitchType.CHORD:
            p_a = 0.9497
            c_i_a = musical_event.get_C_i_chord()
        elif pitch_type is PitchType.SEMITONE:
            p_a = 0.0145
            c_i_a = musical_event.get_C_i_semitone()
        elif pitch_type is PitchType.WHOLETONE:
            p_a = 0.0224
            c_i_a = musical_event.get_C_i_wholetone()
        elif pitch_type is PitchType.OCTAVE:
            p_a = 0.0047
            c_i_a = musical_event.get_C_i_octave()
        elif pitch_type is PitchType.RESIDUAL:
            p_a = 0.0086
            c_i_a = musical_event.get_C_i_residual()

        joint_prob *= p_a / len(c_i_a)  # maybe floating point errors.

    return joint_prob

def onset_time_probability(t_n, i_n, s_n, i_prev, s_prev, v, t_prev):
    """
    :param t_n: onset time of n-th note
    :param i_n: nth musical event
    :param s_n: number of notes played at nth musical event
    :param i_prev: previous musical event
    :param s_prev: number of notes played at previous musical event
    :param v: tempo
    :param t_prev: array of all previous onset times.
    :return: Probability of onset time of nth note.
    """

    w1 = 0.5
    w2 =  0.5
    n = len(t_prev)     # maybe off by one

    if s_n == 1:
        return (w1 * P_IOI1(t_n - t_prev[i_prev.onset_time], i_n, i_prev, v, i_n.note_value)) + (w2 * P_IOI2(t_n - t_prev[n-1], i_n, i_prev, v, i_n.note_value))
    else:
        return P_IOI3(t_n - t_prev[n-1], i_n, i_prev, v) if i_n == i_prev else 0

def P_IOI1(dt, i_n, i_prev, v, V_i):
    """
    Calculates the Inter-Onset Interval type 1
    :param dt: t_n - t_{n-s[n-1]} (see definition of IOI1)
    :param i_n: musical event i
    :param i_n_minus_1: musical event i-1
    :param v: tempo
    :param V_i: note value (half, quarter, whole, etc...)
    :return: probability according to corresponding distribution
    """

    # Straight transition
    if i_n == i_prev + 1:
        return cauchy.pdf(dt, v * V_i, 0.4)
    else:
        return cauchy.pdf(dt, v * V_i, 0.4)


def P_IOI2(dt, i_n, i_prev, v, V_i):
    if i_n == i_prev + 1:
        return cauchy.pdf(dt, (v * V_i) - dev, 0.4)
        # dev is how much we missed the expected note length of event i
        # the expected note length of event i is given by the number of notes times the average IOI of all those notes.

def P_IOI3(dt, pitch_type):

    if pitch_type == PitchType.CHORD:
        return expon.pdf(dt, 0, 0.0101)
