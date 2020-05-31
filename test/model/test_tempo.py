from src.model.tempo import KalmanFilter
import matplotlib.pyplot as plt
import numpy as np

ERROR_MAX_THRESHOLD = 1.5
ERROR_MIN_THRESHOLD = 0.5


def test_kalman_filter():
    """
    Generate observed tempos using gaussian noise and check to see that error is between max and min
    as the filtered values should not exactly copy the generated data but should not be too far off.
    This is not a foolproof way of validating this since it's performance is fairly subjective
    :return:
    """
    kalman_filter = KalmanFilter(60)
    for _ in range(100):
        true_tempos = [60, 65, 62, 63, 64, 65, 60, 65, 65, 66, 67, 68, 68, 68, 68, 68, 68, 68]
        observed_tempos = [tempo + np.random.normal(0, 1) for tempo in true_tempos]
        filter_values = [kalman_filter.next_measurement(tempo) for tempo in observed_tempos]

        error_noise = [abs(observed_tempos[i] - filter_values[i]) for i in range(len(true_tempos))]
        assert np.mean(error_noise) < ERROR_MAX_THRESHOLD
        assert np.mean(error_noise) > ERROR_MIN_THRESHOLD

    plt.plot(observed_tempos, color="green")
    plt.plot(filter_values, color="red")
    plt.xlabel("nth observation")
    plt.ylabel("Tempo")
    plt.legend(["observed tempos", "estimated tempo"])
    plt.title("Tempo Adjustment Test")
    plt.show()
