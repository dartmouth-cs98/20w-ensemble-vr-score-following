import numpy as np
import sys

import pytest

sys.path.append('../../')

from src.music.score import Pieces
from src.model.model import Model

LENGTH_THRESHOLD = 3


@pytest.mark.parametrize("piece,tempo,recording", [
    (Pieces.TestTwinkle, 60, "../../res/data/Twinkle_Recording.npy"),
    (Pieces.TestPachabels, 60, "../../res/data/Pachabels_Recording.npy"),
])
def test_pieces_integration(piece, tempo, recording):
    """
    Sample audio from recording and put into model.
    :param piece: pieces object
    :param tempo: int beats per minute
    :param recording: str path to recording
    :return:
    """
    model = Model(None, piece=piece, tempo=tempo)

    t = 0
    q = np.load(recording)[:, :]
    states = [0] * model.score.N

    while t < len(q[0]):
        obs = q[:, t]
        current_state, prob = model.next_observation(obs)
        t += 1

        if prob < 1.0e-110:
            model.alpha *= 1.0e100

        states[current_state[0]] += 1

    res = states[1:len(states) - 1]
    desired_note_length = (model.recording_speed * model.score.sub_beat.value) / tempo
    average_note_length = sum(res) / len(res)

    # Check no notes were skipped
    assert all(count > 0 for count in res)
    # Check that average note length was within acceptable range
    assert abs(average_note_length - desired_note_length) < LENGTH_THRESHOLD
