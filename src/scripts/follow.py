from src.model.follower import Follower
import logging

from src.music.score import Pieces

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    follower = Follower(with_headset=True, piece=Pieces.ShortPachabels, bpm=60, local_ip="192.168.0.5", port=4000)
    follower.follow()
