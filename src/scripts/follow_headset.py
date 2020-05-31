import argparse
import logging
import sys

sys.path.append("../../")

from src.model.follower import Follower

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Follow playing with headset')
    parser.add_argument('local_ip', metavar='local_ip', type=str, help='Local IP address for connecting to server')
    parser.add_argument('port', metavar='port', type=int, help='Port for connecting to server')

    args = parser.parse_args()

    follower = Follower(with_headset=True, local_ip=args.local_ip, port=args.port)
    follower.follow()
