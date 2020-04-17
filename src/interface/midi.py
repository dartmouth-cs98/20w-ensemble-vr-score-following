from music21 import *
from pretty_midi import *

class MidiClient:

    def __init__(self):

        pass


    def load_file(self, filename):
        midi_data = pretty_midi.PrettyMIDI(filename)
        midi_data.get_onsets()

        mf = midi.MidiFile()
        mf.open(filename)
        mf.read()
        mf.close()
        pass


    def estimate_parameters(self):
        pass


client = MidiClient()
client.load_file('../../res/Dataset/01_Jupiter_vn_vc/Sco_01_Jupiter_vn_vc.mid')