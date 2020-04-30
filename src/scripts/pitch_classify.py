import sys

sys.path.append('../../')

from src.music.note import Pitch
from src.scripts.follow import RecordThread

import numpy as np

from scipy.stats import multivariate_normal

from src.interface.audio import AudioClient
from src.model.model import Model

if __name__ == "__main__":
    audio_client = AudioClient()
    model = Model(audio_client)
    live = True

    if live:
        record_thread = RecordThread(audio_client)
        record_thread.start()

        i = 0
        while True:
            pitch = -1
            pitch_sp = -1
            prob = 0
            prob_sp = 0
            obs = audio_client.q.get().squeeze()

            for k in range(-1, 12):
                obs_prob = model.multivariate_norm_pdf(obs, model.mu[str(k)], str(k))
                if obs_prob > prob:
                    pitch = k
                    prob = obs_prob

            print(Pitch(pitch).name, i, prob)
            i += 1

    else:

        t = 0
        q = np.load("../../res/data/Twinkle_Recording.npy")[:, 32:]

        while t < len(q[0]):
            obs = q[:, t]
            pitch = -1
            pitch_sp = -1
            prob = 0
            prob_sp = 0

            for k in range(-1, 12):
                obs_prob_sp = multivariate_normal.pdf(obs, model.mu[str(k)], model.Sigma[str(k)])
                if obs_prob_sp > prob_sp:
                    pitch_sp = k
                    prob_sp = obs_prob_sp

                obs_prob = model.multivariate_norm_pdf(obs, model.mu[str(k)], str(k))
                if obs_prob > prob:
                    pitch = k
                    prob = obs_prob

            print(Pitch(pitch).name, Pitch(pitch_sp).name, t, obs_prob - obs_prob_sp)
            t += 1
