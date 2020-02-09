"""
Test code for MIDI file reading from the below repository.

https://github.com/mido/mido/blob/stable/examples/midifiles/print_midi_file.py
"""
import sys
from mido import MidiFile

if __name__ == '__main__':
    filename = sys.argv[1]

    midi_file = MidiFile(filename)

    for i, track in enumerate(midi_file.tracks):
        sys.stdout.write('=== Track {}\n'.format(i))
        for message in track:
            sys.stdout.write('  {!r}\n'.format(message))