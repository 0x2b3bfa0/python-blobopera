from fractions import Fraction
from typing import List, Optional, Sequence, Tuple, Type

import music21  # type: ignore
import proto  # type: ignore
from more_itertools import split_before, windowed_complete

from .languages import GenericLanguage, Language
from .phoneme import Phoneme
from .theme import Theme

__protobuf__ = proto.module(package=__name__)


class TimedPhoneme(proto.Message):
    """Syllable Timed Phoneme - protocol buffer message.

    This class represents a timed phoneme, which, basically, holds a member of
    the :class`.phoneme.Phoneme` enumeration along with some sort of duration
    in an unknown unit of time.

    Note:
        Not to be mistaken with :py:class:`.libretto.TimedPhoneme`, which
        serves to a completely different purpose and has different fields.


    Attributes:
        phoneme (Phoneme): The phoneme to utter.
        duration (float): Duration, whose purpose is yet unknown. Empirically,
            changing this value to anything else than 0.1 for vowels may cause
            blobs to sing out of tune.
    """

    phoneme = proto.Field(Phoneme, number=1, optional=True, json_name="name")
    duration = proto.Field(proto.FLOAT, number=2, optional=True)


class Syllable(proto.Message):
    """Note Syllable - protocol buffer message.

    This class represents a syllable consisting of a vowel followed by a suffix
    formed by one or more consonants. Syllables not adhering to these rules
    may lead to unexpected sound and articulation issues.

    Attributes:
        vowel (Phoneme): The initial vowel that will
            support the pitch of the note.
        suffix (Sequence[Phoneme]): The consonants that may
            follow the specified vowel.
    """

    vowel = proto.Field(TimedPhoneme, number=1, optional=True)
    suffix = proto.RepeatedField(TimedPhoneme, number=2, optional=True)

    @classmethod
    def from_phonemes(
        self, phonemes: Optional[List[Phoneme]] = None, duration: float = 0.1
    ):
        """Create a syllable with a list of phonemes.

        Arguments:
            phonemes: The phonemes to include in this syllable.
            duration: The duration parameter for each of the created
                timed phonemes; the first phoneme will have this duration,
                and all the subsequent ones will have half the specified value.

        Returns:
            An instance of this class containing all the given phonemes.

        Raises:
            ValueError: If the first phoneme is a consonant.
        """

        if not phonemes:
            phonemes = [Phoneme.SILENCE]
        if len(phonemes) == 1:
            phonemes.append(phonemes[0])

        if phonemes[0].is_consonant():
            raise ValueError("malformed syllable")

        # Convert all the phonemes to timed phonemes. Note that
        # suffix phonemes should have half the duration of the vowel,
        # so we divide all the durations and fix the vowel later.
        timed_phonemes = [
            TimedPhoneme(phoneme=phoneme, duration=duration / 2)
            for phoneme in phonemes
        ]

        new = self(vowel=timed_phonemes[0], suffix=timed_phonemes[1:])
        new.vowel.duration = duration  # Ignore the halving; see above.
        return new

    def to_phonemes(self) -> List[Phoneme]:
        """Extract all the phonemes from this syllable.

        Returns:
            All the phonemes from this syllable, in the same order that would
            be used to utter them.
        """
        # FIXME: https://github.com/googleapis/proto-plus-python/issues/179
        return [Phoneme(timed.phoneme) for timed in (self.vowel, *self.suffix)]


class Note(proto.Message):
    """Part Note - protocol buffer message.

    This class represents a musical note (or rest) with basic attributes like
    pitch, absolute start time and a syllable that defines the vowel formant
    and the following consonants.

    Note:
        Both :py:attr:`pitch` has been declared as a :py:obj:`float` field, but
        it doesn't contain anything but :py:obj:`int` values.

    Attributes:
        time (float): The absolute start offset of the note, in seconds.
        pitch (float): The MIDI pitch of the note, where 0 means C-1 and 127
            means G9, in scientific notation and with 12-tone equal
            temperament.
        syllable (Syllable): The syllable object holding the phonemes that
            should be played along the note.
        controlled (bool): Unknown variable that requires more reverse
            engineering, doesn't seem to have any noticeable effect on the
            sound.
    """

    time = proto.Field(
        proto.FLOAT, number=1, optional=True, json_name="timeSeconds"
    )
    pitch = proto.Field(proto.FLOAT, number=2, optional=True)
    syllable = proto.Field(
        Syllable, number=3, optional=True, json_name="librettoChunk"
    )
    controlled = proto.Field(proto.BOOL, number=4, optional=True)

    @classmethod
    def from_note(
        self,
        note: music21.note.GeneralNote,
        time: float,
        phonemes: Sequence[Phoneme],
        fallback_pitch: Optional[music21.pitch.Pitch] = None,
    ):
        """Create a Blob Opera note from a music21 note or rest.

        Note:
            When providing a chord, this function will automatically select the
            top note and discard the others.

        Arguments:
            note: A music21 note, chord or rest.
            time: The absolute start offset of the note, in seconds.
            phonemes: The phonemes that define the note lyrics fragment.
            fallback_pitch: The pitch to use for rests. Using the default value
                will abruply stop the vocal generation and cause a short low
                hum prior to the rest, so it's better to use the pitch from the
                previous note to achieve a better decay.

        Returns:
            An instance of this class containing the basic information required
            to play the given note.

        Raises:
            ValueError: If the provided :py:obj:`music21.note.GeneralNote` is
                not a :py:obj:`music21.note.Note`, a
                :py:obj:`music21.note.Rest` nor a :py:obj:`music21.note.Chord`
        """
        result = self()
        result.time = time
        result.syllable = Syllable.from_phonemes(phonemes)

        if type(note) is music21.note.Rest:
            result.pitch = (fallback_pitch or music21.pitch.Pitch(midi=0)).midi
        elif type(note) is music21.note.Note:
            result.pitch = note.pitch.midi
        elif type(note) is music21.chord.Chord:
            result.pitch = note.notes[-1].pitch.midi
        else:
            raise ValueError("found unknown element")

        return result

    def to_note(self) -> music21.note.GeneralNote:
        """Extract the equivalent music21 note for this Blob Opera note.

        Returns:
            A music21 note with an extra ad-hoc attribute holding all the
            phonemes so they can be processed later and converted to strings.
        """
        if Syllable.to_phonemes(self.syllable)[0].is_silence():
            note = music21.note.Rest()
        else:
            note = music21.note.Note()
            note.pitch.midi = self.pitch

        # Unfortunately, timing information is being stored as IEEE 754
        # binary32 single-precision float, so we need to reconstruct the
        # original fraction to the nearest denominator to approximate its
        # real musical duration. This is a humongous HACK and yiends wrong
        # results for durations below the two hundred fifty-sixth note. This
        # duration is small enough to be considered acceptable, but...
        note.offset = Fraction(self.time).limit_denominator(100)

        note.phonemes = Syllable.to_phonemes(self.syllable)
        return note


class Part(proto.Message):
    """Singer Part - protocol buffer message.

    This class represents the "part" that should be interpreted by a single
    "blob" singer, including timing, pitches and lyrics.

    Attributes:
        notes (Sequence[Note]): All the notes that should be played by the
            "blob" singer, including timing, pitches and lyrics.
        start (Sequence[Phoneme]): The consonants that should be emitted prior
            to the first note (vowel) in the part. Due to the nature of the
            data model, there isn't any other way of specifying the start
            consonant as part of the first note in the song.
    """

    notes = proto.RepeatedField(Note, number=1, optional=True)
    start = proto.RepeatedField(
        TimedPhoneme, number=2, optional=True, json_name="startSuffix"
    )

    @classmethod
    def from_part(
        self,
        part: music21.stream.Part,
        language: Type[Language] = GenericLanguage,
        tempo: float = 1.0,
        fill: Phoneme = Phoneme.SILENCE,
    ):
        """Create a Blob Opera part from a music21 part.

        Arguments:
            part: The music21 part.
            language: The absolute start offset of the note, in seconds.
            tempo: The tempo correction factor; 0.5 makes it twice as slow.
            fill: The phoneme to use if none of the notes has lyrics.
        Returns:
            An instance of this class containing the basic information required
            to play the given part.
        """
        notes = (
            event
            for event in part.flat
            if isinstance(event, music21.note.GeneralNote)
        )

        result = self()
        language: Language = language(part)

        # Iterate over the notes while having available a list with all the
        # previous note, the current note, and a list with all the next notes.
        for before, current, after in windowed_complete(notes, 1):
            before, current, after = list(before), current[0], list(after)

            # Use the language parser to obtain the phonemes for the current
            # note. Passing the previous and next notes will allow the parser
            # to infer the sound of a syllable in languages where it may vary
            # depending on its position in a word or the previous/next letters.
            phonemes: list = language.parse(before, current, after)

            # Extract the start consonants so they can be moved to the previous
            # note, as every note must begin with a vowel in order to produce
            # any sound.
            start = []
            while phonemes:
                phoneme = phonemes[0]
                if phoneme.is_vowel():
                    break
                else:
                    start.append(phoneme)
                    phonemes.pop(0)

            # Syllable is only being used for the conversion to timed phonemes.
            timed = Syllable.from_phonemes([Phoneme.SILENCE] + start).suffix

            # XXX Workaround bug in proto-plus
            if not start:
                timed = []

            # If there is a previous note, append the consonants to it. Else,
            # append them to the "start suffix", id est, the part beginning.
            if result.notes:
                result.notes[-1].syllable.suffix.extend(timed)
            else:
                result.start.extend(timed)

            # Prepare the syllables for conversion.
            if isinstance(current, music21.note.Rest):
                syllables = [[Phoneme.SILENCE]]
            elif phonemes:
                # Split the phonemes in small syllables formed by exactly
                # a single start vowel optionally followed by all the
                # immediately subsequent consonants ("amare" -> "am" "ar" "e").
                syllables = list(split_before(phonemes, Phoneme.is_vowel))
                for syllable in syllables:
                    for phoneme in syllable:
                        if phoneme.is_vowel():
                            fill = phoneme  # FIXME: optimize performance.
            else:
                syllables = [[fill]]

            # The length of the original note will be divided in equally sized
            # parts to accomodate each of these syllable fragments. Resorting
            # to the example above, a quarter note would be divided into a
            # quaver triplet with the same pitch, holding each one the
            # corresponding syllable fragment.
            for index, syllable in enumerate(syllables):
                duration = current.quarterLength / len(syllables)
                time = (current.offset + index * duration) / tempo

                # Try to determine a fallback pitch for filling the decay time
                # before rests, so there isn't a low hum.
                if result.notes:
                    last = result.notes[-1].pitch
                    fallback = music21.pitch.Pitch(midi=last)
                else:
                    fallback = None

                note = Note.from_note(current, time, syllable, fallback)
                result.notes.append(note)

        return result

    def to_part(self, name: str = "") -> music21.stream.Part:
        """Extract the equivalent music21 part for this Blob Opera part.

        Arguments:
            name: The name of the part, e.g. "Soprano".

        Returns:
            A music21 part with all the notes in this Blob Opera part, along
            with the raw phonemes as lyrics, in uppercase.
        """
        # Convert each Blob Opera note to a music21 note.
        notes = [note.to_note() for note in self.notes]

        # Prepend the start phonemes to the first note.
        if notes:
            # FIXME: https://github.com/googleapis/proto-plus-python/issues/179
            start = [Phoneme(timed.phoneme) for timed in self.start]
            notes[0].phonemes[:0] = start  # Extend from the beginning.

        # Migrate consonants from previous rests to the actual notes.
        for current, note in enumerate(notes):
            # Determine whether the current "note" is a rest.
            if note.phonemes and note.phonemes[0].is_silence():
                # Find the next "real" note to transfer the consonants.
                for real in range(current, len(notes)):
                    if (lyric := notes[real].phonemes) and lyric[0].is_vowel():
                        # Prepend the consonants to the found note.
                        new = filter(Phoneme.is_consonant, note.phonemes)
                        notes[real].phonemes[:0] = list(new)
                        break
                # Clear the phonemes from the rest.
                notes[current].phonemes = []

        # Convert all the phonemes in each note to textual lyrics. The
        # ``phonemes`` attribute is not part of the music21.note.GeneralNote
        # class; we create it on the fly from ``Note.to_note()`` instead.
        for note in notes:
            lyric = (
                phoneme.name
                for phoneme in note.phonemes
                if not phoneme.is_silence()
            )
            note.lyric = "".join(lyric) or None

        # Start building a music21 part with the provided name.
        part = music21.stream.Part()
        part.partName = name

        # Calculate note and rest durations by subtracting the absolute start
        # time of the current note to the absolute start time of the next note.
        for note, next_note in zip(notes, notes[1:]):
            note.quarterLength = next_note.offset - note.offset
            part.append(note)

        # We can't determine the duration of the last note, as there isn't
        # any further element to subtract the duration from, so we append it
        # directly, assuming the default duration of a quarter note (1 second
        # at 60 beats per minute)
        if notes:
            part.append(notes[-1])

        # Add a metronome mark so quarter notes last a second.
        metronome = music21.tempo.MetronomeMark(number=60)
        metronome.durationToSeconds(music21.duration.Duration(1.0))
        part.insert(0, metronome)

        return part


class Recording(proto.Message):
    """Blob Opera Recording - protocol buffer message.

    This class represents a recording as per the Blob Opera parlance.
    Recordings hold all the required information to "perform" a piece of music
    for each "blob" singer (part).

    Attributes:
        theme (Theme): The user interface theme to use when displaying the
            blobs in the recording player.
        parts (Sequence[Part]): All the four parts of the recording: soprano,
            alto, tenor and bass; in that order.
    """

    theme = proto.Field(Theme, number=1, optional=True)
    parts = proto.RepeatedField(Part, number=2, optional=True)

    @classmethod
    def from_score(
        self,
        score: music21.stream.Score,
        theme: Theme = Theme.NORMAL,
        language: Type[Language] = GenericLanguage,
        tempo: float = 1.0,
        parts: Tuple[int] = (0, 0, 0, 0),
        fill: Phoneme = Phoneme.SILENCE,
    ):
        """Create a Blob Opera recording from a music21 score.

        Arguments:
            score: A music21 score with one or more parts.
            theme: The user interface theme for the Blob Opera experiment.
            language: The language class used for converting lyrics to
                language-agnostic phonemes.
            tempo: The tempo factor to use when interpreting the score, where
                2.0 would mean twice as quick and 0.5 twice as slow.
            parts: The indexes for the four parts that should be used as
                soprano, alto, tenor and bass, in that order. Indexes use the
                same notation as Python indexes, where 0 means the topmost
                part and -2 the penultimate (second from the bottom) part.
            fill: The phoneme used to fill parts that don't have lyrics.

        Returns:
            An instance of this class containing a Blob Opera recording
            representing the provided score.

        Raises:
            ValueError: If the part index tuple contains more or less than
                the expected four elements, as there are exactly four blob
                singers and producing a different number of parts could crash
                the player.
            IndexError: If one of the part indexes is out of bounds when
                retrieving a part from the input :py:data:`score`.
        """
        if len(parts) != 4:
            raise ValueError("recordings require exactly four tracks")
        try:
            recording = Recording(theme=theme)
            for index in parts:
                part = Part.from_part(
                    score.parts[index],
                    language,
                    tempo,
                    fill,
                )
                recording.parts.append(part)
        except IndexError:
            raise IndexError("track index out of bounds")
        else:
            return recording

    def to_score(
        self, title: str = "", composer: str = ""
    ) -> music21.stream.Score:
        """Extract the equivalent music21 score for this Blob Opera recording.

        Arguments:
            title: The recording title, shown in the heading of the score when
                exported to compatible formats, like MusicXML.
            composer: The composer name, shown in the bottom-right corner of
                the heading of the score; idem.

        Returns:
            A music21 score with an approximate
            representation of the recording.
        """
        names = ("Soprano", "Alto", "Tenor", "Bass")
        parts = [part.to_part(name) for part, name in zip(self.parts, names)]

        # Calculate the length of the longer part.
        maximum = max(part.highestTime for part in parts)

        # Pad shorter parts with a rest.
        for part in parts:
            if part.highestTime < maximum:
                rest = music21.note.Rest(offset=part.highestTime)
                rest.duration.quarterLength = maximum - part.highestTime
                part.append(rest)

        metadata = music21.metadata.Metadata(composer=composer, title=title)
        score = music21.stream.Score([metadata] + parts)
        return score
