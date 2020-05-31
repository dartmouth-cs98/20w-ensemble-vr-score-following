import argparse
import logging
import sys

sys.path.append("../../")

from src.model.follower import Follower
from src.music.score import Pieces

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Follow playing without headset')
    parser.add_argument('piece', metavar='piece', type=str, help='Name of piece to be played')
    parser.add_argument('tempo', metavar='tempo', type=int, help='Tempo in bpm (quarter note)')
    args = parser.parse_args()

    piece = Pieces(args.piece)

    follower = Follower(with_headset=False, piece=piece, bpm=60)
    follower.follow()
