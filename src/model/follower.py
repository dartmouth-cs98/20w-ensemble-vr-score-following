import threading
import numpy as np
import sys
import time
import queue

from src.interface.headset import HeadsetClient, MessageBuilder
from src.music.note import Note, Pitch

sys.path.append('../../')

from src.music.score import Pieces
from src.utils.calculations import MathHelper
from src.interface.audio import AudioClient

from src.model.tempo import KalmanFilter
from src.model.model import Model
from src.model.accompaniment import AccompanimentService


class RecordThread(threading.Thread):
    def __init__(self, audio_client, save=False):
        super().__init__()
        self.audio_client = audio_client
        self.save = save

    def run(self):
        print("Starting Recording Thread")
        self.audio_client.record()

        if self.save:
            recording = np.concatenate(self.audio_client.q, axis=1)
            np.save("Pachabels_Recording", recording)


class HeadSetCommThread(threading.Thread):
    def __init__(self, follower):
        super().__init__()
        self.follower = follower

    def run(self):
        while True:
            message = self.follower.output_q.get()
            self.follower.headset_client.send(message)


class Follower:
    """
    Class that wraps together all the components needed to perform score following.
    """

    def __init__(self, with_headset: bool, piece: Pieces):
        self.audio_client = AudioClient()
        self.model = Model(self.audio_client, piece=piece, tempo=60)
        self.accompaniment = AccompanimentService(self.model.score)
        self.tempo = KalmanFilter(self.model.score.tempo)
        self.math_helper = MathHelper()

        # self.live = True
        # self.timed = False

        self.prev_state = None
        self.prev_note_val = None
        self.duration = 1

        self.with_headset = with_headset
        if self.with_headset:
            self.headset_client = HeadsetClient("192.168.0.5", 4000)
            self.output_q = queue.Queue()

    def _reset_probabilities(self, prob):
        """
        Resets probabilities in alpha table if they get too small to prevent underflow
        :param prob: Probability returned by model
        :return: None
        """
        if prob < 1.0e-110:
            self.model.alpha *= 1.0e100

    def _play_accompaniment(self, current_state):
        """
        Play accompaniment given current state
        :param current_state: state predicted by model
        :return: None
        """
        if self.prev_state is not None and current_state[0] - self.prev_state <= 2 and current_state[
            0] - self.prev_state >= 0:
            note_event = current_state[0]
            self.accompaniment.play_accompaniment(note_event)

    def _update_tempo(self, current_state):
        """
        Calculate expected duration of played note and compare/adjust to expected tempo
        :return: None
        """

        # calculate how many frames per beat were observed in the last note
        if current_state[0] > 1 and current_state[0] != self.model.score.N and self.duration > 0:
            prev_expected_duration = self.model.score.notes[self.prev_note_val].duration if type(
                self.model.score.notes[self.prev_note_val - 1].duration) is int else self.model.score.notes[
                self.prev_note_val - 1].duration
            observed_fpb = (self.duration) * (1 / prev_expected_duration)  # This might be one off.
            observed_tempo = self.audio_client.frames_per_min / observed_fpb
            print("Observed Tempo: ", observed_tempo)

            # perform kalman filter update.
            if abs(observed_tempo - self.model.score.tempo) < 20:
                self.tempo.next_measurement(observed_tempo)
                if abs(self.tempo.current_estimate - self.model.score.tempo) > 5 and abs(
                        self.tempo.current_estimate - self.model.score.tempo) < 60:
                    self.model.score.tempo = self.tempo.current_estimate
                    self.model.update_tempo()

    def _get_observation(self, i):
        """
        Get observation from queue
        :param i:
        :return:
        """
        if i == 0:
            return self.model.mu["2"]  # Bullshit note to set alpha correctly.
        else:
            return self.audio_client.q.get()

    def _send_accompaniment_to_headset(self, current_state):
        message = MessageBuilder.build_accompaniment_message(self.model.score.parts[:, current_state[0]])
        self.output_q.put(message)
        pass

    def follow(self):
        ts = time.time()
        print("Start time: ", ts)
        try:
            record_thread = RecordThread(self.audio_client)
            record_thread.start()

            if self.with_headset:
                headset_thread = HeadSetCommThread(self)
                headset_thread.start()

            i = 0
            while True:
                # Get observation from audio client queue and perform forward algorithm step
                obs = self._get_observation(i)
                current_state, prob = self.model.next_observation(obs)
                print(current_state, prob, self.duration, self.tempo.current_estimate)
                i += 1

                self._reset_probabilities(prob)
                if not self.with_headset:
                    self._play_accompaniment(current_state)
                else:
                    self._send_accompaniment_to_headset(current_state)

                # get true event of current state, i.e. the half note when sub-beat is eighth.
                played_note_val = self.model.score.get_true_note_event(current_state[0])
                if self.prev_state is None:
                    self.prev_state = current_state[0]
                    self.prev_note_val = self.model.score.get_true_note_event(self.prev_state)
                    continue
                else:
                    self.prev_note_val = self.model.score.get_true_note_event(self.prev_state)

                # Have we moved onto the next note
                if played_note_val == self.prev_note_val:
                    self.duration += 1
                    self.prev_state = current_state[0]
                else:
                    self._update_tempo(current_state)

                    self.duration = 0
                    self.prev_state = current_state[0]
                    self.prev_note_val = played_note_val
        finally:
            print("Time Elapsed: ", time.time() - ts)


if __name__ == "__main__":
    follower = Follower(with_headset=False, piece=Pieces.ShortPachabels)
    follower.follow()
