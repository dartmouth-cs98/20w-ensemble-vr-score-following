from src.model.follower import Follower
import logging
logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    follower = Follower()
    follower.follow()

