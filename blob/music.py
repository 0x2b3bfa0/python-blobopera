import json

import music21

from dataclasses import dataclass
from typing import Optional, List, Iterator, Tuple

from .languages import Language, Generic
from .lyrics import Syllable, Suffix
from .phonemes import Timed, Phoneme
from .themes import Theme


@dataclass
class Score:
    """Full choral score with four voices (soprano, alto, tenor and bass), as
    required by the Blob Opera audio engine.

    >>> Score(music21.converter.parse('file.musicxml')).data()
    {...}
    """

    stream: music21.stream.Stream
    theme: Theme = Theme.NORMAL
    language: Language = Generic
    tempo: float = 1.0
    tracks: Tuple[int] = (0,0,0,0)
    fill: Phoneme = Phoneme.SIL

    def __post_init__(self):
        if not all(
            -(length := len(self.stream.parts)) <= track < length
            for track in self.tracks
        ):
            raise ValueError("track index out of bounds")
        self.parts = [
            Part(self.stream.parts[track], self.language, self.tempo)
            for track in self.tracks
        ]

    def data(self) -> dict:
        return {
            "theme": self.theme.value,
            "parts": [part.data() for part in self.parts],
        }

@dataclass
class Part:
    """Single pentagram (part) of the vocal score, including
    pitches, times and lyrics.

    >>> Part(part=parse('file.musicxml').parts[0], language=Generic)
    <Part object at ...>
    """

    part: music21.stream.Part
    language: Language
    tempo: float
    fill: Phoneme = Phoneme.SIL

    def __post_init__(self):
        start, sounds = [], []
        events = list(self.events())
        last: Phoneme = self.fill

        # Relocate consonants so every syllable starts with a vowel
        for index, _ in enumerate(events):
            # If the current event is not a rest
            if events[index].get("phonemes") is not None:
                # If the current event has phonemes inside
                if events[index]["phonemes"] and len(events[index]["phonemes"]) > 0 :
                    # Relocate start consonants to the previous note or rest

                    while len(events[index]["phonemes"]) > 0 and not events[index]["phonemes"][0].vowel():
                        phoneme = events[index]["phonemes"].pop(0)
                        # If the part begins with a consonant, set the start
                        if index == 0:
                            start.append(phoneme)
                        # If the previous event has phonemes, append this
                        elif events[index - 1].get("phonemes"):
                            events[index - 1]["phonemes"].append(phoneme)
                        # Else, the previous event is empty; move anyways
                        else:
                            syllable = [Phoneme.SIL, phoneme]
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
                duration = event["duration"] / len(syllables)

                # Add all the syllables with the same pitch to the sounds list
                for position, syllable in enumerate(syllables):
                    if event:
                        sounds.append(event)
                    else:
                        sounds.append(
                            {
                            "time": event["time"] + position * duration,
                            "duration": duration,
                            "phonemes": syllable,
                            }
                        )
            else:
                # The current event is a rest; append it
                sounds.append(event)

        # Update the class variables with the pertaining object representations
        self.sounds = []
        for sound in sounds:
            # sound = {**val}
            sound['time'] =  sound["time"] * (1 / self.tempo)
            self.sounds.append(Sound(**sound))

        self.start = Suffix(start)

    def events(self) -> Iterator[List]:
        """Yield notes and rests along with their start times and lyrics."""
        language: Language = self.language(self.part.flat)

        for index, item in enumerate(self.part.flat.secondsMap):
            if type(item["element"]) is music21.note.Rest:
                yield {
                    "time": item["offsetSeconds"],
                    "duration": item["durationSeconds"],
                }
            elif type(item["element"]) is music21.note.Note:
                phonemes = language.parse(
                    item["offsetSeconds"],
                    item["element"].lyric,
                    index
                )
                yield {
                    "time": item["offsetSeconds"],
                    "duration": item["durationSeconds"],
                    "pitch": item["element"].pitch.midi,
                    "phonemes": phonemes or [],
                }

    def data(self) -> dict:
        return {
            "notes": [sound.data() for sound in self.sounds],
            "startSuffix": self.start.data(),
        }


@dataclass
class Sound:
    """Single sound (or lack thereof) starting in 'time', with
    the specified MIDI pitch and the phonemes that form a syllable.

    >>> Sound(time=10.0, pitch=63, phonemes=[Phoneme["A"]], controlled=False)
    <Sound object at ...>
    """

    time: float
    duration: float
    phonemes: Optional[List[Phoneme]] = None
    pitch: Optional[int] = 0
    controlled: bool = False

    def __post_init__(self):
        # Create a syllable from the phonemes; first phoneme must be a vowel
        self.syllable = Syllable(self.phonemes, strict=True)

    def data(self) -> dict:
        return {
            "timeSeconds": self.time,
            "midiPitch": self.pitch,
            "controlled": self.controlled,
            "librettoChunk": self.syllable.data(),
        }
