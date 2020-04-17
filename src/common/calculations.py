import math
import pickle
import numpy as np

class MathHelper:
    def __init__(self):
        with open("../../res/data/tempo_args.pkl", 'rb') as pickle_file:
            self.args = pickle.load(pickle_file)

    @staticmethod
    def fpb_to_tempo(y, a, b, c, d):
        """
        Given how many frames a beat is supposed to last, returns approximate tempo for system.
        :param y: how many frames a beat is supposed to last
        :param a:
        :param b:
        :param c:
        :param d:
        :return:
        """
        return (np.log((y - d) / (a)) / (-c)) + b

    @staticmethod
    def tempo_to_fpb(x, a, b, c, d):
        return a * np.exp(-c * (x - b)) + d

    def bpm_to_prob(self, desired_bpm, beat_value, recording_speed=570):
        desired_fpb = recording_speed/(desired_bpm)  * (beat_value)
        system_tempo = MathHelper.fpb_to_tempo(desired_fpb, *self.args)
        return 1 - (system_tempo / recording_speed)


