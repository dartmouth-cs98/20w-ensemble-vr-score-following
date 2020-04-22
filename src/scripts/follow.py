import threading
import numpy as np
import sys
import time

sys.path.append('../../')

from src.common.calculations import MathHelper
from src.model.tempo import KalmanFilter

from src.music.score import Pieces

from src.interface.audio import AudioClient
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
            np.save("Twinkle_Recording", recording)


if __name__ == "__main__":
    audio_client = AudioClient()
    model = Model(audio_client, piece="ASDF", tempo=60)
    accompaniment = AccompanimentService(model.score)
    tempo = KalmanFilter(model.score.tempo)
    math_helper = MathHelper()

    live = True
    timed = True

    prev_state = None
    duration = 1

    if live:
        record_thread = RecordThread(audio_client)
        record_thread.start()

        i = 0
        if timed:
            t_end = time.time() + 10
            while time.time() < t_end:
                obs = audio_client.q.get()
                current_state, prob = model.next_observation(obs)
                print(current_state, prob)
                i += 1
            print("Num Frames: ", i)

        else:
            while True:
                obs = audio_client.q.get()
                current_state, prob = model.next_observation(obs)
                i += 1
                print(current_state, prob, duration, tempo.current_estimate)

                # # get true event of current state, i.e. the half note when sub-beat is eighth.
                # played_note_val = model.score.get_true_note_event(current_state[0])
                # if prev_state is None:
                #     prev_state = current_state[0]
                #     prev_note_val = model.score.get_true_note_event(prev_state)
                #     continue
                # else:
                #     prev_note_val = model.score.get_true_note_event(prev_state)
                #
                # print(current_state, prob, duration, tempo.current_estimate)
                #
                # if played_note_val == prev_note_val:
                #     duration += 1
                # else:
                #     if current_state[0] > 1 and current_state[0] != model.score.N and duration > 0:
                #         # calculate how many frames per beat were observed in the last note
                #         observed_fpb = duration * (1 / model.score.sub_beat.value) * (
                #                     model.score.sub_beat.value / model.score.notes[prev_note_val].duration.value)   # This might be one off.
                #         observed_tempo = audio_client.frames_per_min / observed_fpb
                #         print("Observed Tempo: ", observed_tempo)
                #
                #         # perform kalman filter update.
                #         tempo.next_measurement(observed_tempo)
                #         if abs(tempo.current_estimate - model.score.tempo) > 5:
                #             model.score.tempo = tempo.current_estimate
                #             model.initialize_transition_matrix()
                #
                #     duration = 0
                #     prev_state = current_state[0]
                #     prev_note_val = played_note_val

                # note_event = current_state[0]
                # accompaniment.play_note(note_event)

    else:
        t = 0
        q = np.load("../../res/data/Twinkle_Recording.npy")[:, :]

        while t < len(q[0]):
            obs = q[:, t]
            current_state, prob = model.next_observation(obs)
            print(current_state, t, prob)
            t += 1
