import matplotlib.pyplot as plt
import numpy as np


class KalmanFilter:

    def __init__(self, current_estimate, estimate_error=100 ** 2, measurement_error=10 ** 2, kalman_gain=None,
                 process_noise_var=100):
        self.observations = []
        self.kalman_gain = kalman_gain
        self.estimate_uncertainty = estimate_error + process_noise_var
        self.measurement_error = measurement_error
        self.current_estimate = current_estimate
        self.prev_estimate = current_estimate
        self.process_noise_var = process_noise_var

    def calc_kalman_gain(self):
        self.kalman_gain = self.estimate_uncertainty / (self.estimate_uncertainty + self.measurement_error)
        return self.kalman_gain

    def create_estimate(self, measurement):
        self.current_estimate = self.prev_estimate + self.kalman_gain * (measurement - self.prev_estimate)
        self.prev_estimate = self.current_estimate
        return self.current_estimate

    def update_error(self):
        self.estimate_uncertainty = (self.measurement_error * self.estimate_uncertainty) / (
                self.measurement_error + self.estimate_uncertainty) + self.process_noise_var
        return self.estimate_uncertainty

    def next_measurement(self, measurement):
        self.calc_kalman_gain()
        self.create_estimate(measurement)
        self.update_error()
        return self.current_estimate


if __name__ == "__main__":
    kalman_filter = KalmanFilter(60)

    true_tempos = [60, 65, 62, 63, 64, 65, 60, 65, 65, 66, 67, 68, 68, 68, 68, 68, 68, 68]
    observed_tempos = [tempo + np.random.normal(0, 1) for tempo in true_tempos]
    filter_values = [kalman_filter.next_measurement(tempo) for tempo in observed_tempos]

    plt.plot(observed_tempos, color="green")
    plt.plot(filter_values, color="red")
    plt.xlabel("nth observation")
    plt.ylabel("Tempo")
    plt.legend(["observed tempos", "estimated tempo"])
    plt.title("Tempo Adjustment Test")
    plt.show()
