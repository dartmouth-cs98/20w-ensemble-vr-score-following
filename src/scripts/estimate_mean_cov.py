from src.client.AudioClient import AudioClient
import pickle
import numpy as np

if __name__ == "__main__":
    import time

    for i in range(12):
        input("Press Return to Begin Recording for Pitch {0}".format(i))
        time.sleep(2)
        client = AudioClient()
        client.record(plot=True, time=10)
        mean, cov = client.estimate_mean_covariance()

        np.save("res/mean_{0}".format(i), mean)
        np.save("res/cov_{0}".format(i), cov)

    input("Press Return to Begin Recording for Silence")
    time.sleep(2)
    client = AudioClient()
    client.record(plot=True, time=10)
    mean, cov = client.estimate_mean_covariance()

    np.save("res/mean_-1", mean)
    np.save("res/cov_-1", cov)

