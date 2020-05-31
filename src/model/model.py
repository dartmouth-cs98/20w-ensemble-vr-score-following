import logging
import sys

from src.music.note import Pitch

sys.path.append('../../')

import os
import numpy as np
from numpy.linalg import det, inv
from src.utils.calculations import MathHelper
from src.music.score import Pieces, ScoreFactory

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class Model:

    def __init__(self, audio_client, tempo=None, instrument="violin", piece=Pieces.TestTwinkle):
        self.piece = piece
        self.score = ScoreFactory.get_score(piece)
        if tempo is not None:
            self.score.tempo = tempo
        self.L = 1
        self.N = self.score.N

        self.NUM_PITCHES = 13

        self.audio_client = audio_client
        self.math_helper = MathHelper()

        self.a = np.zeros((self.N + 1, self.L, self.N + 1, self.L))  # transition matrix
        self.pi = np.zeros((self.N + 1, self.L))  # initial probabilities matrix
        self.e = np.zeros((self.N + 1, self.L))  # exit probabilities matrix

        # probability of pitch errors. Eq(17) Section IVB2.
        self.C = 1.0e-50
        # probability of entering break state, 1 * 10^{-x} for some positive x
        self.s = 1.0e-1000
        # probability of resuming performance, uniform for all N
        self.r = 1 / (2 * self.N)
        # probability of deletion error
        self.p_del = 1.0e-75
        self.pause_self_loop = 0.996

        # Used when calculating self loop probabilities. Different from audio client fpm
        self.recording_speed = 1140

        self.instrument = instrument

        self.MEAN_COV_DIR = f"{THIS_DIR}/../../res/"
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
        self.initialize_pitch_weights()
        self.initialize_indexers()

        logging.info("Model Initialized")

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
        """
        Calculate Inverse and determinant for covariance matrices for each pitch.
        inv_mat - N x 13 x 12 x 12
        det_mat - N x 13
        mu - N x 13 x 12
        y_t - N x 13 x 12

        13 is number of pitches, 12 is size of array that gets returned, cause 12 notes in octave.
        :return:
        """
        for pitch in self.Sigma:
            self.inv_det[pitch] = (inv(self.Sigma[pitch]), det(self.Sigma[pitch]))

        inv_mat = np.zeros((self.NUM_PITCHES, 12, 12))  # num pitches by (12,12) inv of covariance
        det_mat = np.zeros(self.NUM_PITCHES)  # num pitches
        mu_mat = np.zeros((self.NUM_PITCHES, 12))  # num_pitches by
        for pitch in self.inv_det:
            index = int(pitch) + 1
            inv_mat[index, :, :] = self.inv_det[pitch][0]
            det_mat[index] = self.inv_det[pitch][1]
            mu_mat[index, :] = self.mu[pitch]

        self.inv_mat = np.array([inv_mat] * (self.N + 1))
        self.det_mat = np.array([det_mat] * (self.N + 1))
        self.mu_mat = np.array([mu_mat] * (self.N + 1))

    def initialize_pitch_weights(self):
        """
        Initializes the weights that will be multiplied with the pdf's for each note in the score.
        weights represent how likely we should see a note in a certain event.
        i.e. if the expected note is a C, there's a small chance of hearing a different note.
        :return:
        """
        pitches = [self.score.subdivided_notes[i].pitch.value for i in range(self.N)]
        pitches.append(Pitch.REST.value)  # break state
        pause_state_w = np.array(
            [[self._get_weight(k, Pitch.REST.value) for k in range(self.NUM_PITCHES)]] * (self.N + 1))
        zero_state_w = np.array([[self._get_weight(k, p_i) for k in range(self.NUM_PITCHES)] for p_i in pitches])

        if self.L == 1:
            self.pitch_weights = np.stack([zero_state_w], axis=2)
        else:
            self.pitch_weights = np.stack([zero_state_w, pause_state_w], axis=2)

    def parse_piece(self):
        """
        Initializes self loop probabilities a_{0,0}
        :return:
        """

        np.fill_diagonal(self.a[:, 0, :, 0],
                         self.math_helper.bpm_to_prob(self.score.tempo, beat_value=self.score.sub_beat.value,
                                                      recording_speed=self.recording_speed))
        self.a[self.N, 0, self.N, 0] = self.pause_self_loop

    def initialize_transition_matrix(self):
        """
        initializes transition matrix 'a'
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

            for j in range(self.N):
                if j - i > 2 or j - i < 0:  # j not in nbh(i)
                    self.a[i, 0, j, 0] = self.e[i, 0] * self.s * self.r * self.pi[
                        j, 0]  # Eq. 12 (j and i are backwards)

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
        self.e[self.N, 0] = 1 - self.a[self.N, 0, self.N, 0]

    def initialize_indexers(self):
        """
        Initializes matrices to help quickly index for alpha and a during forward algorithm steps.
        :return:
        """
        self.a_indices = np.arange((self.N + 1) * (self.N + 1) * self.L * self.L).reshape(
            (self.N + 1, self.L, self.N + 1, self.L))
        self.a_indexer = np.vstack([[self.a_indices[i - 2:i + 1, :, i, :]] for i in range(2, self.N + 1)])
        self.alpha_indexer = np.arange(3 * self.L).reshape((3, self.L))[None, :] + self.L * np.tile(
            np.vstack(np.arange(self.N - 1)), self.L)[:, None]

    def _get_a(self):
        """
        Use indexer to build the "a" for the transition prob term of the forward algorithm step. (Eq.21)
        a_{(j,l),(i,l)}
        :return:
        """
        first_event_a = np.zeros((3, self.L, 1, self.L))
        first_event_a[0, :, 0, :] = self.a[0:1, :, 0, :]

        second_event_a = np.zeros((3, self.L, 1, self.L))
        second_event_a[0:2, :, 0, :] = self.a[0:2, :, 1, :]

        a_rest = self.a.flatten()[self.a_indexer]
        a_full = np.vstack(
            ([first_event_a.reshape(3, self.L, self.L)], [second_event_a.reshape(3, self.L, self.L)], a_rest))
        a_full[self.N, :, :, :] = 0
        pause_state_a = self.a[:, :, self.N, :]

        return a_full, pause_state_a

    def _get_alpha(self):
        """
        Use indexer to build the "alpha" for the transition prob term of the forward algorithm step. (Eq.21)
        alpha_{(t-1)(j,l)}
        :return:
        """
        first_event_alpha = np.zeros((3, self.L))
        first_event_alpha[0, :] = self.alpha[0:1, :]

        second_event_alpha = np.zeros((3, self.L))
        second_event_alpha[0:2, :] = self.alpha[0:2, :]

        alpha_rest = self.alpha.flatten()[self.alpha_indexer]
        alpha_full = np.vstack(([first_event_alpha], [second_event_alpha], alpha_rest))
        alpha_full[self.N, :, :] = 0

        pause_state_alpha = np.zeros((1, self.L))
        pause_state_alpha[0, :] = self.alpha[self.N, :]

        return alpha_full, pause_state_alpha

    def b(self, y_t):
        """
        Probability of observing audio feature y_t at bottom state l of top state i
        :return: L x N matrix representing probability of observing current observation for eacn of the N events.
        """

        y_t = np.array([[y_t] * self.NUM_PITCHES] * (self.N + 1))
        pdf = np.clip(MathHelper.multivariate_norm_pdf(y_t, self.mu_mat, self.det_mat, self.inv_mat), 0, 0.999)
        pdf[self.N] = np.clip(pdf[self.N], 0, 0.001)
        return np.sum(np.stack([pdf] * self.L, axis=2) * self.pitch_weights, axis=1)

    def _get_weight(self, k, p_i):
        """
        Get value of w_k,0
        :param k:
        :param p_i:
        :return:
        """
        if p_i == -1:
            if k == 0:
                return 1 - self.C
            else:
                return 0
        elif (p_i == -1 and k != 0) or k == 0:
            return 0.0
        else:
            offset = min(min(abs(k - 1 - p_i), (14 - p_i) + k - 1), (14 - k - 1) + p_i)
            if offset == 0:
                return 1 - self.C
            elif offset == 1:
                return 0.175
            elif offset == 2:
                return 0.270 * self.C
            elif offset == 7 or offset == 5:
                return 0.055 * self.C
            else:
                return 0

    def next_observation(self, obs):
        """
        Implements another iteration of forward algorithm
        Updates belief state of what the current music event is
        :return:
        """
        if self.t == 0:
            self.alpha = self.b(obs) * self.pi
            self.t += 1
            return np.unravel_index(np.argmax(self.alpha), self.alpha.shape), np.max(self.alpha)
        else:
            # Get emission probability
            obs_prob = self.b(obs)

            # Build neighborhooded alpha and a.
            a_full, pause_state_a = self._get_a()
            alpha_full, pause_state_alpha = self._get_alpha()

            # calculate probability of making transition and probability of going through the break state
            trans_prob = np.sum(np.stack([alpha_full] * self.L, axis=3) * a_full, axis=(1, 2))
            trans_pause = np.sum((np.stack([pause_state_alpha] * self.L, axis=2) * pause_state_a), axis=(0, 1))
            stop_state_prob = np.stack([np.sum(self.alpha[self.N, :] * self.a[self.N, :, 0, :], axis=1)] * (self.N + 1))
            trans_prob += stop_state_prob
            trans_prob[self.N, :] = trans_pause

            # update alpha
            self.alpha = obs_prob * trans_prob
            return np.unravel_index(np.argmax(self.alpha), self.alpha.shape), np.max(self.alpha)

    def update_tempo(self):
        """
        Updates the self-loop probabilities as well as other transitions to reflect current tempo.
        The only things that get affected are self loop and i+1 transition.
        :return:
        """
        self.parse_piece()
        next_state_prob = 1 - self.s - np.diag(self.a[:, 0, :, 0]) - np.pad(np.diag(self.a[:, 0, 2:, 0]), (0, 2),
                                                                            'constant')
        next_state_prob = self.e * np.stack([next_state_prob] * self.L, axis=1) * np.stack([self.pi[:, 0]] * self.L,
                                                                                           axis=1)
        np.fill_diagonal(self.a[:, 0, 1:, 0], next_state_prob[:, 0])
        if self.L > 1:
            np.fill_diagonal(self.a[:, 1, 1:, 0], next_state_prob[:, 1])
