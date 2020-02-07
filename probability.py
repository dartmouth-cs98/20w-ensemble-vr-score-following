from enum import Enum

import numpy as np
from scipy.stats import cauchy


class PitchType(Enum):
    CHORD = "chord",
    SEMITONE = "semitone",
    WHOLETONE = "wholetone",
    OCTAVE = "octave",
    OTHER = "other"


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


def pitch_probability(pitch, pitch_type, num_same_type):
    """
    :param pitch: MIDI value of the pitch
    :param pitch_type: type of pitch (See PitchType Enum)
    :param num_same_type: number of pitches of same pitch type as "pitch" in musical event i = "c_i^A
    :return:
    """

    p_a = 0
    if pitch_type is PitchType.CHORD:
        p_a = 0.9497
    elif pitch_type is PitchType.SEMITONE:
        p_a = 0.0145
    elif pitch_type is PitchType.WHOLETONE:
        p_a = 0.0224
    elif pitch_type is PitchType.OCTAVE:
        p_a = 0.0047
    else:
        p_a = 0.0086


    return p_a / num_same_type


def onset_time_probability():

    pass

def P_IOI1(dt, i_n, i_n_minus_1, v, V_i):
    """
    Calculates the Inter-Onset Interval type 1
    :param dt: t_n - t_{n-s[n-1]} (see definition of IOI1)
    :param i_n: musical event i
    :param i_n_minus_1: musical event i-1
    :param v: tempo
    :param V_i: note value (half, quarter, whole, etc...)
    :return: probability according to corresponding distribution
    """
    if i_n == i_n_minus_1 + 1:
        return cauchy.pdf(dt, v * V_i, 0.4)


def P_IOI2(dt, i_n, i_n_minus_1, v):
    pass

def P_IOI3(dt, i_n, i_n_minus_1, v):
    pass
