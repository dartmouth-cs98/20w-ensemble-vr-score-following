import sys
sys.path.append('../../')

from src.music.note import Duration
from src.music.score import ScoreBuilder

builder = ScoreBuilder('../../res/midi/Pachabels/Pachelbels_Canon_in_D_String_Quartet.mid', Duration(0.25))
score = builder.build()

print(score)
