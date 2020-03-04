from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import queue
import sys
import librosa
import librosa.display

class AudioClient:
    """
    Class that handles input from microphone
    """

    def __init__(self, sample_rate=44100, window=200, channels=[1], downsample=10, interval=30):
        self.sample_rate = sample_rate
        self.window = window
        self.channels = channels
        self.downsample = downsample
        self.interval = interval
        self.mapping = [c - 1 for c in self.channels]  # Channel numbers start with 1
        self.q = queue.Queue()
        self.lines = None
        self.plotdata = None
        self.continue_recording = True

    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)

        data = indata.copy().squeeze()
        # self.q.put(librosa.core.cqt(data, sr=self.sample_rate))
        self.q.put(librosa.feature.chroma_cqt(y=data, sr=self.sample_rate))


    def record(self, plot=False):
        stream = sd.InputStream(channels=1, callback=self.audio_callback, blocksize=2048, samplerate=self.sample_rate)
        with stream:
            while self.continue_recording:
                print(self.q.qsize())

        if plot:
            while not self.q.empty():
                data = self.q.get()
                librosa.display.specshow(data, y_axis='chroma', x_axis='time')
                plt.show()

    def stop_recording(self):
        self.continue_recording = False;


client = AudioClient()
client.record()