import queue
import sys

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd


class AudioClient:
    """
    Class that handles input from microphone
    """

    def __init__(self, sample_rate=44100, window=200, channels=[1], downsample=10, interval=30, blocksize=2048):
        self.sample_rate = sample_rate
        self.window = window
        self.channels = channels
        self.downsample = downsample
        self.interval = interval
        self.blocksize = blocksize
        self.mapping = [c - 1 for c in self.channels]  # Channel numbers start with 1
        self.q = queue.Queue()
        self.lines = None
        self.plotdata = None
        self.continue_recording = True
        self.frames_per_min = 570

    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)

        data = indata.copy().squeeze()
        cqt = librosa.feature.chroma_cqt(y=data, sr=self.sample_rate)
        cqt = np.mean(cqt, axis=1).reshape((cqt.shape[0], 1))
        self.q.put(cqt.squeeze())

    def record(self, plot=False, time=0):
        stream = sd.InputStream(channels=1, callback=self.audio_callback, blocksize=self.blocksize,
                                samplerate=self.sample_rate)
        with stream:
            if time == 0:
                print("Press Return to Stop Recording")
                input()
                self.continue_recording = False
            else:
                sd.sleep(time * 2000)

        if plot:
            full_plot = np.concatenate(self.q, axis=1)
            librosa.display.specshow(full_plot, y_axis='chroma', x_axis='time')
            plt.colorbar()
            plt.set_cmap("bwr")
            plt.show()

    def stop_recording(self):
        self.continue_recording = False

    def estimate_mean_covariance(self):
        full_plot = np.concatenate(self.q, axis=1)
        sample_mean = np.mean(full_plot, axis=1).reshape((full_plot.shape[0], 1))
        sample_cov = np.cov(full_plot)

        print("Mean:", sample_mean)
        print("Cov: ", sample_cov)
        return sample_mean, sample_cov


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
