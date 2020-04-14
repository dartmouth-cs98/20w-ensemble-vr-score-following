import os

import numpy as np
from numpy.linalg import det, inv

from src.common.calculations import MathHelper
from src.model.Score import Pieces, ScoreFactory


class Model:

    def __init__(self, audio_client, tempo=None, instrument="violin", piece=Pieces.Twinkle):
        self.piece = piece
        self.score = ScoreFactory.get_score(piece)
        if tempo != None:
            self.score.tempo = tempo
        self.L = 1
        self.N = self.score.N

        self.audio_client = audio_client
        self.math_helper = MathHelper()

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
        self.inv_det = {}
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

        # Load mean
        directory = os.fsencode(base_path + "/mean/")
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            note = filename.split('_')[1].split('.')[0]
            self.mu[note] = np.load(base_path + "/mean/" + filename).squeeze()

        # Load covariance
        directory = os.fsencode(base_path + "/cov")
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            note = filename.split('_')[1].split('.')[0]
            temp = np.load(base_path + "/cov/" + filename).squeeze()
            self.Sigma[note] = np.zeros(temp.shape)
            np.fill_diagonal(self.Sigma[note], np.diag(temp))

        # Load silence
        self.mu["-1"] = np.load(base_path + "/mean/mean_-1.npy").squeeze()
        temp = np.load(base_path + "/cov/cov_-1.npy").squeeze()
        self.Sigma["-1"] = np.zeros(temp.shape)
        np.fill_diagonal(self.Sigma["-1"], np.diag(temp))

        self.initialize_inv_det()

    def initialize_inv_det(self):
        for pitch in self.Sigma:
            self.inv_det[pitch] = (inv(self.Sigma[pitch]), det(self.Sigma[pitch]))

    def parse_piece(self):
        """
        Initializes self loop probabilities a_{0,0}
        :return:
        """

        for i, note in enumerate(self.score.notes):
            self.a[i, 0, i, 0] = self.math_helper.bpm_to_prob(self.score.tempo, beat_value=self.score.sub_beat.value,
                                                              recording_speed=570)

        self.a[self.N, 0, self.N, 0] = 0.996

    def initialize_transition_matrix(self):
        """
        intializes transition matrix 'a'
        where a[j,l',i,l] represents the transition probabilities of the standard HMM
        from top state j bottom state l' to top state i bottom state l
        :return:
        """

        self.parse_piece()

        if self.L == 2:
            self.a[:, 1, :, 0] = 0  # a_{1,0}
            self.a[:, 1, :, 1] = 0.999  # a_{1,1}
            self.a[:, 0, :, 1] = 1.0e-100  # a_{0,1}

        for i in range(self.N):

            self.initialize_exit_probabilities(i)

            if i < self.N - 2:
                self.a[i, :, i + 2, 0] = self.e[i, :] * self.p_del * self.pi[i + 2, 0]  # a_{i, i+2}
            if i < self.N - 1:
                next_state_prob = 1 - self.s - self.a[i, 0, i, 0] - self.a[i, 0, i + 2, 0]
                self.a[i, :, i + 1, 0] = self.e[i, :] * next_state_prob * self.pi[i + 1, 0]  # a_{i, i+1}

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
        self.pi[:, 1:] = 0
        self.pi[self.N, 0] = 1

    def initialize_exit_probabilities(self, i):
        """
        Initialize exit probabilities from bottom states
        :param i:
        :return:
        """
        self.e[i, :] = 1 - np.sum(self.a[i, :, i, :], axis=1)
        self.e[self.N, 0] = 0.004  # = 1 - a^{N}_0,0

    def b(self, y_t, i, l):
        """
        Probability of observing audio feature y_t at bottom state l of top state i
        :return:
        """
        if i == self.N or l == 1:
            pdf = self.multivariate_norm_pdf(y_t, self.mu["-1"], "-1")
            return 0.999 if pdf > 1 else pdf
        elif l == 0:
            prob = 0
            p_i = self.score.notes[i].pitch.value
            for k in self.K:
                w = self.get_weight(int(k), p_i)
                pdf = self.multivariate_norm_pdf(y_t, self.mu[k], k)
                if pdf > 1:
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
            return 0.175
        elif offset == 2:
            return self.C * 0.270
        elif offset == 7 or offset == 5:
            return self.C * 0.055
        else:
            return 0

    def multivariate_norm_pdf(self, x, mu, pitch):
        k = x.shape[-1]
        den = np.sqrt((2 * np.pi) ** k * self.inv_det[pitch][1])
        x = x - mu
        return np.squeeze(np.exp(-x[..., None, :] @ self.inv_det[pitch][0] @ x[..., None] / 2)) / den

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
