"""Generic language.

This language module aims to achieve a good enough universal phoneme conversion
if there isn't a better alternative.
"""
import re
import unicodedata
from typing import List

import music21  # type: ignore

from ..phoneme import Phoneme
from .language import Language


class GenericLanguage(Language):
    """Convert lyrics to phonemes with simple 1-to-1 string matching.

    Warning:
        Unknown characters will be silently dropped.
    """

    def __init__(self, part: music21.stream.Part, *, strict: bool = False):
        """Initialize the language with the complete part stream.

        Note:
            With the complete stream, the parser can look around and take
            decisions based on the surrounding lyrics, like altering a phoneme
            based on the previous and next ones.

        Arguments:
            part: The whole part of the score.
            strict: If true, don't allow events with multiple lyrics.
        """
        self.part, self.strict = part, strict

    def parse(
        self, before: List[dict], current: dict, after: List[dict]
    ) -> List[Phoneme]:
        """Parse lyrics from the given event.

        This parser doesn't understand the language and just tries to extract
        phonemes with a regular expression from the event's lyrics fragment.

        Arguments:
            before: A list with all the previous events.
            current: The current event.
            after: A list with all the next events.

        Returns:
            A list of phonemes representing the lyrics for the current event.

        Raises:
            ValueError: If  :py:attr:`self.strict` is :py:obj:`True`
                and there are alternative lyrics for the given event.
        """

        if lyrics := current.lyric:
            # Scores can contain many lines of lyrics. That's not supported.
            if "\n" in lyrics and self.strict:
                raise ValueError("each note must contain at most one lyric")

            # Retrieve the first line of lyrics.
            lyrics = lyrics.splitlines()[0]

            # Extract the lowercase text of each phoneme.
            phonemes = [phoneme.name.lower() for phoneme in Phoneme]

            # Sort phonemes by length and build a regular expression.
            expression = "|".join(sorted(phonemes, reverse=True, key=len))
            # Find and capture all the phonemes in the normalized text.
            matches = re.findall(f"({expression})", self.normalize(lyrics))

            # Return a list of phoneme objects with all the matches.
            return [Phoneme[match.upper()] for match in matches]
        else:
            return []

    def normalize(self, text: str) -> str:
        """Normalize text.

        This function converts the given text to lowercase, replaces non-ASCII
        characters by their normalized variants, and removes both punctuation
        and whitespace.

        Example:
            >>> normalize("Té; xt")
            "text"

        Arguments:
            text: Any unicode string.

        Returns:
            The normalized ASCII text.
        """
        # Convert to lowercase.
        text = text.casefold()

        # Normalize non-ASCII characters.
        text = unicodedata.normalize("NFD", text)
        text = text.encode("ascii", "ignore").decode("utf-8")

        # Return only the alphabetic characters.
        return re.sub("[^a-z]", "", text)
