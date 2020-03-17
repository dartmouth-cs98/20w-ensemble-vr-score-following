import pretty_midi, math

E4 = pretty_midi.Note(start=2.00000, end=3.997917, pitch=64)
sr = 2
start_idx = E4.start * sr
end_idx = math.ceil(E4.end * sr)

