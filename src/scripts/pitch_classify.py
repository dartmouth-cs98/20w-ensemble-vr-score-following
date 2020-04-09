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
    q = np.load("Twinkle_Recording.npy")[:, :]

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

            obs_prob = model.mvnormpdf(obs, model.mu[str(k)], model.Sigma[str(k)], str(k))
            if obs_prob > prob:
                pitch = k
                prob = obs_prob

        print(Pitch.__dict__["_member_names_"][pitch], Pitch.__dict__["_member_names_"][pitch_sp], t,
              obs_prob - obs_prob_sp)
        t += 1
