"""Random language.

This language module provides random lyrics as seen in the default Blob Opera
carols. It should be avoided, whenever desirable, in favor of actual lyrics.
"""
import random
from typing import Callable, List

import music21  # type: ignore

from ..phoneme import Phoneme
from .language import Language


class RandomLanguage(Language):
    """Generate random phonemes for parts without lyrics.

    Note:
        Actual singers do exactly this sometimes, but don't tell anybody,
        it's our secret.
    """

    def __init__(self, part: music21.stream.Part, *, strict: bool = False):
        """Initialize the language with the complete part stream.

        This class doesn't use the part stream at all, but we take it anyways
        so it conforms to the protocol.

        Arguments:
            part: The whole part of the score.
            strict: If true, don't allow events with multiple lyrics.
        """
        self.random = random.Random()
        self.strict = strict
        self.part = part

    def parse(
        self, before: List[dict], current: dict, after: List[dict]
    ) -> List[Phoneme]:
        """Generate lyrics for the given event.

        This parser returns pseudorandom vowel-consonant pairs based on the
        start offset of each note, so all the four parts have a consistent
        vocalization when singing together.

        Arguments:
            before: A list with all the previous events.
            current: The current event.
            after: A list with all the next events.

        Returns:
            A list of phonemes representing the lyrics for the current event.

        Raises:
            ValueError: If :py:attr:`self.strict` is :py:obj:`True` and
                the provided event already contains lyrics.
        """
        # It doesn't make too much sense to replace lyrics with random lyrics.
        if current.lyric is not None and self.strict:
            raise ValueError("random language doesn't accept lyrics")

        # Seed the pseudorandom generator with the absolute note start time.
        self.random.seed(current.offset)

        # Return a random vowel and a random consonant.
        return [self.pick(Phoneme.is_vowel), self.pick(Phoneme.is_consonant)]

    def pick(self, condition: Callable[[Phoneme], bool]) -> Phoneme:
        """Pick a random phoneme that meets the specified condition.

        This function picks random phonemes repeatedly and stops when finds one
        that meets the specified condition.

        Arguments:
            condition: a callable that returns True when a given phoneme
                meets the desired conditions.

        Returns:
            A phoneme meeting the specified condition.
        """
        while not condition(phoneme := self.random.choice(list(Phoneme))):
            pass
        return phoneme
