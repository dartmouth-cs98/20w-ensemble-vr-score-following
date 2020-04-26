import pickle
import numpy as np

class MathHelper:
    def __init__(self):
        with open("../../res/data/tempo_args_1.pkl", 'rb') as pickle_file:
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
        """
        Given how many minutes per beat, returns score tempo.
        :param x: minutes per beat = recording speed (frames per minute) / frames per beat
        :param a:
        :param b:
        :param c:
        :param d:
        :return:
        """
        return a * np.exp(-c * (x - b)) + d

    def bpm_to_prob(self, desired_bpm, beat_value, recording_speed=570):
        desired_fpb = recording_speed/(desired_bpm)  * (beat_value)
        system_tempo = MathHelper.fpb_to_tempo(desired_fpb, *self.args)
        return 1 - (system_tempo / recording_speed)

    @staticmethod
    def multivariate_norm_pdf(x, mu, det, inv):
        k = x.shape[-1]
        den = np.sqrt((2 * np.pi) ** k * det)
        np.subtract(x, mu, x)
        return np.squeeze(np.exp(-x[..., None, :] @ inv @ x[..., None] / 2)) / den
