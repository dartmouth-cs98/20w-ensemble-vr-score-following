"""
Test code for MIDI file reading from the below repository.
"""
import sys
from mido import MidiFile
from midiTimeline import TimeLine



if __name__ == '__main__':
    filename = sys.argv[1]

    midi_file = MidiFile(filename)

    time_line = TimeLine(midi_file)
    time_line.gen_time_line()
    print(time_line.get_time_line())