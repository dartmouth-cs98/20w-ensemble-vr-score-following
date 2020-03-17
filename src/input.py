import sounddevice as sd
import queue
import librosa
import librosa.display
import matplotlib.pyplot as plt

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy().squeeze())


if __name__ == "__main__":
    sr = 44100

    q = queue.Queue()
    downsample = 10
    channels = [1]
    mapping = [c - 1 for c in channels]
    duration = 2  # seconds

    with sd.InputStream(channels=1, callback=callback, blocksize=2048, samplerate=sr):
        sd.sleep(int(duration * 1000))


    print(q.qsize())
    while not q.empty():
        data = q.get()
        chroma_cqt = librosa.feature.chroma_cqt(y=data, sr=sr)

        librosa.display.specshow(chroma_cqt, y_axis='chroma', x_axis='time')
        plt.colorbar(format='%+2.0f dB')
        plt.show()


