import music21
import pretty_midi

from src.music.note import Note, Duration, Pitch


class MidiClient:
    """
    Class that loads and parses midi files into tracks
    """

    def __init__(self, beats_per_measure=4):
        self.midi_file = None
        self.beats_per_measure = beats_per_measure
        pass

    def load_file(self, filename):
        mf = music21.midi.MidiFile()
        mf.open(filename)
        mf.read()
        mf.close()
        self.midi_file = mf

    def parse_track(self, track_num, is_solo=True):
        """
        Parses the given track and returns a list of note objects
        * Solo part will use Pitch enum for pitch
        * Accompaniment parts will use midi number for pitch.
        * Long notes > 4 beats will get split into 4 beats + the rest of the note.
        :param track_num:
        :param is_solo:
        :return:
        """
        notes = []
        track = self.midi_file.tracks[track_num]
        for i in range(1, len(track.events) - 1):
            event = track.events[i]
            delta_time = track.events[i + 1]

            if delta_time.time is not None and delta_time.time > 1:
                if event.type != "NOTE_ON" or event.velocity == 0:
                    pitch = Pitch.REST
                else:
                    if is_solo:
                        pitch = Note.note_name_to_pitch_enum(pretty_midi.note_number_to_name(event.pitch))
                    else:
                        pitch = event.pitch

                num_beats = round(delta_time.time / self.midi_file.ticksPerQuarterNote, 2)
                while num_beats > 4:        # while num beats is greater than beats left in bar.
                    notes.append(Note(pitch, Duration(4).value))
                    num_beats -= 4

                if num_beats > 0:
                    notes.append(Note(pitch, Duration(num_beats).value))
        return notes