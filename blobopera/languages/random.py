import random
from typing import List, Optional

import music21

from ..phoneme import Phoneme
from .language import Language


class Random(Language):
    """Generate random phonemes for parts without any lyrics."""

    def __init__(self, part: music21.stream.Part, *, strict: bool = False):
        """Initialize the language with the complete stream, so parsers
        can look around and take decisions based on the surrounding lyrics.
        """
        self.part, self.strict = part, strict

    def parse(
        self, time: float, lyrics: Optional[str], index: int
    ) -> Optional[List[Phoneme]]:
        """Parse the given lyrics and return random vowel-consonant pairs.

        >>> parse(None)
        [<Phoneme.I: 8>, <Phoneme.C: 2>]
        """
        if lyrics and self.strict:
            raise ValueError("random language doesn't accept lyrics")

        random.seed(time)
        while not (vowel := random.choice(Phoneme)).vowel():
            pass
        while not (consonant := random.choice(Phoneme)).consonant():
            pass

        return [vowel, consonant]
