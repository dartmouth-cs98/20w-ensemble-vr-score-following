import numpy as np
import os
from scipy.stats import multivariate_normal

from src.model.Score import Pieces, ScoreFactory


class Model:

    def __init__(self, audio_client, instrument="violin", piece=Pieces.Twinkle):
        self.piece = piece
        self.L = 2
        self.N = piece.N
        self.audio_client = audio_client

        self.a = np.zeros((self.N + 1, self.L, self.N + 1, self.L))  # transition matrix
        self.pi = np.zeros((self.N + 1, self.L))  # initial probabilities matrix
        self.e = np.zeros((self.N + 1, self.L))  # exit probabilities matrix

        # proability of pitch errors. Eq(17) Section IVB2.
        self.C = 1.0e-50
        # probability of entering break state, 1 * 10^{-x} for some positive x
        self.s = 1.0e-10
        # probability of resuming performance, uniform for all N
        self.r = 1 / self.N
        # probability of deletion error
        self.p_del = 1.0e-50

        self.instrument = instrument

        self.MEAN_COV_DIR = "../../res/"
        self.mu = {}
        self.Sigma = {}
        self.initialize_overtones()
        self.K = [x for x in self.mu]

        self.score = ScoreFactory.get_score(piece)
        self.initialize_initial_probabilities()

    def initialize_overtones(self):
        """
        Load emission probability parameters based on instrument
        :return:
        """
        base_path = self.MEAN_COV_DIR + self.instrument
        directory = os.fsencode(base_path + "/mean/")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            note = filename[-5]
            self.mu[note] = np.load(base_path + "/mean/" + filename)

        directory = os.fsencode(base_path + "/cov")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            note = filename[-5]
            self.Sigma[note] = np.load(base_path + "/cov/" + filename)

        self.mu["-1"] = np.load(base_path + "/mean/mean_-1.npy")
        self.Sigma["-1"] = np.load(base_path + "/cov/cov_-1.npy")

    def parse_piece(self):
        """
        Initializes self loop probabilities a_{0,0}
        :return:
        """

        for i, note in self.piece.notes:
            num_beats = note.duration

            fpb = self.get_frames_per_beat(self.piece.tempo, self.audio_client.sample_rate, self.audio_client.blocksize)
            self.a[i, 0, i, 0] = 1 - 1 / (fpb * num_beats)

        self.a[self.N, 0, self.N, 0] = 0.996

    def initialize_transition_matrix(self):
        """
        intializes transition matrix 'a'
        where a[j,l',i,l] represents the transition probabilities of the standard HMM
        from top state j bottom state l' to top state i bottom state l
        :return:
        """

        self.parse_piece()

        for i in range(self.N):
            self.a[i, 1, i, 0] = 0  # a_{1,0}
            self.a[i, 1, i, 1] = 0.999  # a_{1,1}
            self.a[i, 0, i, 1] = 1.0e-100  # a_{0,1}

            self.initialize_exit_probabilities(i)

            if i < self.N - 2:
                self.a[i, 0, i + 2, 0] = self.e[i, 0] * self.p_del * self.pi[i + 2, 0]  # a_{i, i+2}
                self.a[i, 1, i + 2, 0] = self.e[i, 1] * self.p_del * self.pi[i + 2, 0]
            if i < self.N - 1:
                next_state_prob = 1 - self.s - self.a[i, 0, i, 0] - self.a[i, 0, i + 2, 0]
                self.a[i, 0, i + 1, 0] = self.e[i, 0] * next_state_prob * self.pi[i + 1, 0]  # a_{i, i+1}
                self.a[i, 1, i + 1, 0] = self.e[i, 1] * next_state_prob * self.pi[i + 1, 0]

            for j in range(i, self.N):
                if j - i > 2:  # j not in nbh(i)
                    self.a[i, 0, j, 0] = self.e[j, 0] * self.s * self.r * self.pi[i, 0]  # Eq. 12

            # transition probability to break state eq. 14
            self.a[i, 0, self.N, 0] = self.e[i, 0] * self.s * self.pi[self.N, 0]
            # transition probability away from break state eq.15
            self.a[self.N, 0, i, 0] = self.e[self.N, 0] * self.r * self.pi[i, 0]

    def initialize_initial_probabilities(self):
        """
        Initialize initial probabilities of bottom states.
        :return:
        """
        self.pi[:, 0] = 1
        self.pi[:, 1] = 0
        self.pi[self.N, 0] = 1

    def initialize_exit_probabilities(self, i):
        """
        Initialize exit probabilities from bottom states
        :param i:
        :return:
        """
        for l in range(self.L):
            l_prime_sum = 0
            for lp in range(self.L):
                l_prime_sum += self.a[i, l, i, lp]
            self.e[i, l] = 1 - l_prime_sum

        self.e[self.N, 0] = 0.004 # = 1 - a^{N}_0,0

    def b(self, y_t, i, l):
        """
        Probability of observing audio feature y_t at bottom state l of top state i
        :return:
        """
        if l == 0:
            prob = 0
            p_i = self.score.notes[i].pitch.value
            for k in self.K:
                w = self.get_weight(k, p_i)
                prob += w * multivariate_normal.pdf(y_t, self.mu[k], self.Sigma[k])
        elif l == 1:
            return multivariate_normal.pdf(y_t, self.mu["-1"], self.Sigma["-1"])

    def get_weight(self, k, p_i):
        """
        Get value of w_k,0
        :param k:
        :param p_i:
        :return:
        """
        offset = abs(k - p_i)

        if offset == 0:
            return 1 - self.C
        elif offset == 1:
            return self.C * 0.175
        elif offset == 2:
            return self.C * 0.270
        elif offset == 7:
            return self.C * 0.055
        else:
            return 0

    def decode(self):
        pass

    def get_frames_per_beat(self, bpm, sample_rate, block_size):
        frames_per_minute = (sample_rate / block_size) * 60
        return frames_per_minute / bpm
