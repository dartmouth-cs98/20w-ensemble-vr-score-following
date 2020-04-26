import sys
import time
import fluidsynth

from src.music.note import Pitch
from src.music.score import TwinkleTwinkleScore

sys.path.append('../../')

class AccompanimentService:

    def __init__(self, score):
        self.score = score
        self.fs = fluidsynth.Synth()
        self.fs.start(driver='coreaudio')
        self.sfid = self.fs.sfload("../../res/sounds/SalC5Light2.sf2")
        self.fs.program_select(0, self.sfid, 0, 0)

        self.current_notes = set()
        self.previous_event = None

    def play_note(self, event):
        if event == len(self.score.subdivided_notes):
            return

        if self.previous_event != event:
            self.current_notes.clear()
            self.previous_event = event

        note = self.score.get_accompaniment(event)
        if note == Pitch.REST:
            return

        for playing_notes in self.current_notes:
            if playing_notes != note:
                self.fs.noteoff(0, playing_notes)

        if note not in self.current_notes:
            self.fs.noteon(0, note, 100)
            self.current_notes.add(note)