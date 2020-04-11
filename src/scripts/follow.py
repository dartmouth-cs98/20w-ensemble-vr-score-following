import threading
import numpy as np
import sys
import time

sys.path.append('../../')

from src.client.AudioClient import AudioClient
from src.service.ModelService import Model


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
    model = Model(audio_client)
    live = True
    timed = True

    if live:
        record_thread = RecordThread(audio_client)
        record_thread.start()

        i = 0
        if timed:
            t_end = time.time() + 10
            while time.time() < t_end:
                obs = audio_client.q.get().squeeze()
                current_state, prob = model.next_observation(obs)
                print(current_state, prob)
                i += 1
            print("Num Frames: ", i)

        else:
            while True:
                obs = audio_client.q.get().squeeze()
                current_state, prob = model.next_observation(obs)
                print(current_state, prob)
                i += 1

    else:
        t = 0
        q = np.load("Twinkle_Recording.npy")[:, 32:]

        while t < len(q[0]):
            obs = q[:, t]
            current_state, prob = model.next_observation(obs)
            print(current_state, t, prob)
            t += 1
