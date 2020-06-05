from src.model.tempo import KalmanFilter
import matplotlib.pyplot as plt
import numpy as np

ERROR_MAX_THRESHOLD = 2
ERROR_MIN_THRESHOLD = 0.1


def test_kalman_filter():
    """
    Generate observed tempos using gaussian noise and check to see that error is between max and min
    as the filtered values should not exactly copy the generated data but should not be too far off.
    This is not a foolproof way of validating this since it's performance is fairly subjective
    :return:
    """
    kalman_filter = KalmanFilter(60)
    passed = 0
    for _ in range(100):
        true_tempos = [60, 65, 62, 63, 64, 65, 60, 65, 65, 66, 67, 68, 68, 68, 68, 68, 68, 68]
        observed_tempos = [tempo + np.random.normal(0, 1) for tempo in true_tempos]
        filter_values = [kalman_filter.next_measurement(tempo) for tempo in observed_tempos]

        error_noise = [abs(observed_tempos[i] - filter_values[i]) for i in range(len(true_tempos))]
        passed += 1 if ERROR_MAX_THRESHOLD > np.mean(error_noise) > ERROR_MIN_THRESHOLD else -1
    assert passed >= 98
