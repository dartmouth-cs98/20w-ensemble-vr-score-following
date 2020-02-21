"""
Test code for MIDI file reading.
"""
import sys
import mido
from mido import MidiFile
from midiTimeline import TimeLine



if __name__ == '__main__':
    filename = sys.argv[1]

    midi_file = MidiFile(filename)

    port = mido.open_output('New Port', virtual=True)
    for track in midi_file.tracks:
        for message in track:
            port.send(message)
"""    time_line = TimeLine(midi_file)
    time_line.gen_time_line()
    time_line.play_back()"""