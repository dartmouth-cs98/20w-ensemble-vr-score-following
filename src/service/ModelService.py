import numpy as np
import os

class Model:

    def __init__(self, instrument="violin"):
        self.transition_matrix = None
        self.emission_matrix = None
        self.initial_probabilities = None
        self.N = None

        self.instrument = instrument

        self.MEAN_COV_DIR = "../../res/"
        self.mu = {}
        self.Sigma = {}
        self.initialize_overtones()


    def initialize_overtones(self):
        base_path = self.MEAN_COV_DIR + self.instrument
        directory = os.fsencode(base_path + "/mean/")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            note = filename[-5]
            self.mu[note] = np.load(base_path + "/mean/" + filename)

        directory = os.fsencode(base_path + "/cov")

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            note = filename[-5]
            self.Sigma[note] = np.load(base_path + "/cov/" + filename)

    def b(self):

        pass






    def train(self):
        """
        Learn transition and emission matrix probabilities.
        :return:
        """
        pass

    def decode(self):
        pass



