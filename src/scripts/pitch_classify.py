import sys
sys.path.append('../../')

import numpy as np

from scipy.stats import multivariate_normal

from src.model.Note import Pitch

from src.client.AudioClient import AudioClient
from src.service.ModelService import Model

if __name__ == "__main__":
    audio_client = AudioClient()
    model = Model(audio_client)

    t = 0
    q = np.load("Twinkle_Recording.npy")[:, 50:]

    while t < len(q[0]):
        obs = q[:, t]
        pitch = -1
        prob = 0
        for k in range(-1, 12):
            obs_prob = multivariate_normal.pdf(obs, model.mu[str(k)], model.Sigma[str(k)])
            if obs_prob > prob:
                pitch = k
                prob = obs_prob

        print(Pitch.__dict__["_member_names_"][pitch], t, prob)
        t += 1

