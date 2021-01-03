from typing import Iterator, List, Optional, Tuple

import music21
import proto

from .language import Generic, Language
from .phoneme import Phoneme, Timed
from .theme import Theme

__protobuf__ = proto.module(package=__name__)


class Syllable(proto.Message):
    vowel = proto.Field(Timed, number=1, optional=True)
    suffix = proto.RepeatedField(Timed, number=2, optional=True)

    @classmethod
    def from_phonemes(
        self, phonemes: List[Phoneme] = None, duration: float = 0.1
    ):
        if not phonemes:
            phonemes = [Phoneme.SILENCE]
        if len(phonemes) == 1:
            phonemes += [Phoneme.SILENCE]

        vowel, *suffix = (
            # Suffix phonemes have half the duration of the vowel
            Timed(phoneme=phoneme, duration=duration / (1 + min(index, 1)))
            for index, phoneme in enumerate(phonemes)
        )

        return self(
            vowel=Timed.to_dict(vowel), suffix=map(Timed.to_dict, suffix)
        )

    def to_phonemes(self) -> List[Phoneme]:
        return [Phoneme(timed.phoneme) for timed in (self.vowel, *self.suffix)]

    @staticmethod
    def to_text(phonemes: List[Phoneme]) -> Optional[str]:
        text = "".join(
            phoneme.name for phoneme in phonemes if not phoneme.silence()
        )
        return text or None


class Note(proto.Message):
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
        time: float,
        pitch: int = 0,
        phonemes: Optional[List[Phoneme]] = None,
        controlled: bool = False,
        duration: float = 0.1,
    ):
        return self(
            time=time,
            pitch=pitch,
            syllable=Syllable.to_dict(
                Syllable.from_phonemes(phonemes, duration)
            ),
            controlled=controlled,
        )

    def to_note(self) -> music21.note.GeneralNote:
        if Syllable.to_phonemes(self.syllable)[0].silence():
            note = music21.note.Rest()
        else:
            note = music21.note.Note()
            note.pitch.midi = self.pitch

        note.offset = self.time
        note.lyric = Syllable.to_text(Syllable.to_phonemes(self.syllable))

        return note


class Part(proto.Message):
    notes = proto.RepeatedField(Note, number=1, optional=True)
    start = proto.RepeatedField(
        Timed, number=2, optional=True, json_name="startSuffix"
    )

    @classmethod
    def from_part(
        self,
        stream: music21.stream.Part,
        language: Language = Generic,
        tempo: float = 1.0,
        fill: Phoneme = Phoneme.SILENCE,
        duration: float = 0.1,
        controlled: bool = False,
    ):
        start, sounds = [], []

        # Remove tempo indications to avoid a known bug.
        for index, element in enumerate(stream):
            if isinstance(element, music21.tempo.TempoIndication):
                stream.pop(index)

        events = list(self.generate_events(stream, language, tempo))
        last: Phoneme = fill

        # Relocate consonants so every syllable starts with a vowel
        for index, _ in enumerate(events):
            # If the current event is not a rest
            if events[index].get("phonemes") is not None:
                # If the current event has phonemes inside
                if (
                    events[index]["phonemes"]
                    and len(events[index]["phonemes"]) > 0
                ):
                    # Relocate start consonants to the previous note or rest

                    while (
                        len(events[index]["phonemes"]) > 0
                        and not events[index]["phonemes"][0].vowel()
                    ):
                        phoneme = events[index]["phonemes"].pop(0)
                        # If the part begins with a consonant, set the start
                        if index == 0:
                            start.append(phoneme)
                        # If the previous event has phonemes, append this
                        elif events[index - 1].get("phonemes"):
                            events[index - 1]["phonemes"].append(phoneme)
                        # Else, the previous event is empty; move anyways
                        else:
                            syllable = [Phoneme.SILENCE, phoneme]
                            events[index - 1]["phonemes"] = syllable
                    # Save the last vowel for melismatic parts
                    if len(events[index]["phonemes"]) > 0:
                        last = events[index]["phonemes"][0]
                    else:
                        del events[index]["phonemes"]
                else:
                    # When going through a melisma, repeat the last note
                    events[index]["phonemes"].append(last)

        # Split multiple syllables in subdivided notes of equal length
        for event in events:
            # If the current event is not a rest
            if event.get("phonemes") is not None:
                # Split phonemes in chunks of a vowel plus optional consonants
                syllables = []
                for phoneme in event["phonemes"]:
                    if not phoneme.consonant():
                        syllables.append([])
                    syllables[-1].append(phoneme)

                # Calculate the duration for each of these divisions
                _duration = event["duration"] / len(syllables)

                # Add all the syllables with the same pitch to the sounds list
                for position, syllable in enumerate(syllables):
                    if event:
                        sounds.append(event)
                    else:
                        sounds.append(
                            {
                                "time": event["time"] + position * _duration,
                                "duration": _duration,
                                "phonemes": syllable,
                            }
                        )
            else:
                # The current event is a rest; append it
                sounds.append(event)

        # Update the class variables with the pertaining object representations
        notes = [
            Note.from_note(
                **{
                    key: value
                    for key, value in sound.items()
                    if key != "duration"
                },
                duration=duration,
                controlled=controlled,
            )
            for sound in sounds
        ]
        start = Syllable.from_phonemes(
            [Phoneme.SILENCE] + start, duration
        ).suffix
        return self(notes=map(Note.to_dict, notes), start=start)

    @staticmethod
    def generate_events(
        part: music21.stream.Part, language: type, tempo: float
    ) -> Iterator[List]:
        """Yield notes and rests along with their start times and lyrics."""
        language: Language = language(part.flat)

        for index, item in enumerate(part.flat.secondsMap):
            if type(item["element"]) is music21.note.Rest:
                yield {
                    "time": (1 / tempo) * item["offsetSeconds"],
                    "duration": item["durationSeconds"],
                }
            elif type(item["element"]) is music21.note.Note:
                phonemes = language.parse(
                    (1 / tempo) * item["offsetSeconds"],
                    item["element"].lyric,
                    index,
                )
                yield {
                    "time": (1 / tempo) * item["offsetSeconds"],
                    "duration": item["durationSeconds"],
                    "pitch": item["element"].pitch.midi,
                    "phonemes": phonemes or [],
                }

    def to_part(self) -> music21.stream.Part:
        part = music21.stream.Part()
        notes = [Note.to_note(note) for note in self.notes]

        for note, next_note in zip(notes, notes[1:]):
            note.quarterLength = next_note.offset - note.offset
            part.append(note)
        part.append(notes[-1])

        start = Syllable.to_text(
            Phoneme(timed.phoneme) for timed in self.start
        )

        if start:
            updated = start + part.notesAndRests[0].lyric or ""
            part.notesAndRests[0].lyric = updated

        metronome = music21.tempo.MetronomeMark(number=60)
        metronome.durationToSeconds(music21.duration.Duration(1.0))
        part.insert(0, metronome)
        return part


class Recording(proto.Message):
    theme = proto.Field(Theme, number=1, optional=True)
    parts = proto.RepeatedField(Part, number=2, optional=True)

    @classmethod
    def from_score(
        self,
        score: music21.stream.Score,
        theme: Theme = Theme.NORMAL,
        language: type = Generic,
        tempo: float = 1.0,
        tracks: Tuple[int] = (0, 0, 0, 0),
        fill: Phoneme = Phoneme.SILENCE,
        duration: float = 0.1,
        controlled: bool = False,
    ):
        try:
            parts = (
                Part.from_part(
                    score.parts[track],
                    language,
                    tempo,
                    fill,
                    duration,
                    controlled,
                )
                for track in tracks
            )
        except IndexError:
            raise IndexError("track index out of bounds")
        else:
            return Recording(theme=theme, parts=map(Part.to_dict, parts))

    def to_score(
        self, title: str = "", composer: str = ""
    ) -> music21.stream.Score:
        parts = [part.to_part() for part in self.parts]
        maximum = max(part.highestTime for part in parts)

        for part, name in zip(parts, ("Soprano", "Alto", "Tenor", "Bass")):
            # Compensate shorter parts (if any) with rests.
            if (length := part.highestTime) < maximum:
                rest = music21.note.Rest()
                rest.duration.quarterLength = maximum - length
                rest.offset = length
                part.append(rest)
            # Set the part name.
            part.partName = name

        score = music21.stream.Score(parts)
        score.insert(0, music21.metadata.Metadata())
        score.metadata.composer = composer
        score.metadata.title = title

        return score
