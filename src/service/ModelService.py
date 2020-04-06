import os
import numpy as np
from scipy.stats import multivariate_normal

from src.model.Score import Pieces, ScoreFactory


class Model:

    def __init__(self, audio_client, instrument="violin", piece=Pieces.Twinkle):
        self.piece = piece
        self.score = ScoreFactory.get_score(piece)
        self.L = 2
        self.N = self.score.N
        self.audio_client = audio_client

        self.a = np.zeros((self.N + 1, self.L, self.N + 1, self.L))  # transition matrix
        self.pi = np.zeros((self.N + 1, self.L))  # initial probabilities matrix
        self.e = np.zeros((self.N + 1, self.L))  # exit probabilities matrix

        # proability of pitch errors. Eq(17) Section IVB2.
        self.C = 1.0e-50
        # probability of entering break state, 1 * 10^{-x} for some positive x
        self.s = 1.0e-100
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

        # Forward algorithm variables
        self.t = 0
        self.alpha = np.zeros((self.N + 1, self.L))

        self.initialize_initial_probabilities()
        self.initialize_transition_matrix()

    def initialize_overtones(self):
        """
        Load emission probability parameters based on instrument
        :return:
        """
        base_path = self.MEAN_COV_DIR + self.instrument
        directory = os.fsencode(base_path + "/mean/")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            note = filename.split('_')[1].split('.')[0]
            self.mu[note] = np.load(base_path + "/mean/" + filename).squeeze()

        directory = os.fsencode(base_path + "/cov")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            note = filename.split('_')[1].split('.')[0]
            # self.Sigma[note] = np.load(base_path + "/cov/" + filename).squeeze()
            temp = np.load(base_path + "/cov/" + filename).squeeze()
            self.Sigma[note] = np.zeros(temp.shape)
            np.fill_diagonal(self.Sigma[note], np.diag(temp))

        self.mu["-1"] = np.load(base_path + "/mean/mean_-1.npy").squeeze()

        temp = np.load(base_path + "/cov/cov_-1.npy").squeeze()
        self.Sigma["-1"] = np.zeros(temp.shape)
        np.fill_diagonal(self.Sigma["-1"], np.diag(temp))

    def parse_piece(self):
        """
        Initializes self loop probabilities a_{0,0}
        :return:
        """

        for i, note in enumerate(self.score.notes):
            num_beats = note.duration.value

            fpb = self.get_frames_per_beat(self.score.tempo, self.audio_client.sample_rate, self.audio_client.blocksize)
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

        self.a[:, 1, :, 0] = 0  # a_{1,0}
        self.a[:, 1, :, 1] = 0.999  # a_{1,1}
        self.a[:, 0, :, 1] = 1.0e-100  # a_{0,1}

        for i in range(self.N):

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

        self.e[self.N, 0] = 0.004  # = 1 - a^{N}_0,0

    def b(self, y_t, i, l):
        """
        Probability of observing audio feature y_t at bottom state l of top state i
        :return:
        """
        if i == self.N or l == 1:
            pdf = multivariate_normal.pdf(y_t, self.mu["-1"], self.Sigma["-1"])
            return 0.999 if pdf > 10 else pdf
        elif l == 0:
            prob = 0
            p_i = self.score.notes[i].pitch.value[0]
            for k in self.K:
                w = self.get_weight(int(k), p_i)
                pdf = multivariate_normal.pdf(y_t, self.mu[k], self.Sigma[k])
                if pdf > 10:
                    pdf = 0.999
                prob += w * pdf
            return prob

    def get_weight(self, k, p_i):
        """
        Get value of w_k,0
        :param k:
        :param p_i:
        :return:
        """
        offset = min(min(abs(k - p_i), (12 - p_i) + k), (12 - k) + p_i)

        if offset == 0:
            return 1 - self.C
        elif offset == 1:
            return self.C * 0.175
        elif offset == 2:
            return self.C * 0.270
        elif offset == 7 or offset == 5:
            return self.C * 0.055
        else:
            return 0

    def get_frames_per_beat(self, bpm, sample_rate, block_size):
        frames_per_minute = (sample_rate / block_size) * 60
        return frames_per_minute / bpm

    def next_observation(self, obs):
        """
        Implements another iteration of forward algorithm
        Updates belief state of what the current music event is
        :return:
        """

        if self.t == 0:
            for i in range(self.N + 1):
                for l in range(self.L):
                    self.alpha[i, l] = self.b(obs, i, l) * self.pi[i, l]
            self.t += 1
            return np.unravel_index(np.argmax(self.alpha), self.alpha.shape), np.max(self.alpha)
        else:
            new_alpha = np.zeros((self.N + 1, self.L))
            for i in range(self.N + 1):
                nbh = max(-i, -2)

                for l in range(self.L):
                    if i < self.N:
                        new_alpha[i, l] = self.b(obs, i, l) * (
                                np.sum(self.alpha[i + nbh:i + 1, :] * self.a[i + nbh:i + 1, :, i, l])
                                + np.sum(self.alpha[self.N, :] * self.a[self.N, :, i, l]))
                    elif i == self.N:
                        new_alpha[i, l] = self.b(obs, i, 0) * (np.sum(self.alpha[self.N, :] * self.a[:, :, self.N, l]))

            self.alpha = new_alpha

            return np.unravel_index(np.argmax(self.alpha), self.alpha.shape), np.max(self.alpha)
