import re
import unicodedata

import music21

from abc import abstractmethod
from typing import Protocol, Optional, List

from .phonemes import Phoneme


class Language(Protocol):
    @abstractmethod
    def __init__(self, part: music21.stream.Part):
        pass

    @abstractmethod
    def parse(lyrics: Optional[str]) -> Optional[List[Phoneme]]:
        pass


class Generic(Language):
    def __init__(self, part: music21.stream.Part, *, strict: bool = False):
        """Initialize the language with the complete stream, so parsers
        can look around and take decisions based on the surrounding lyrics.
        """
        self.part, self.strict = part, strict

    def parse(self, lyrics: Optional[str], index: int) -> Optional[List[Phoneme]]:
        """Parse the given lyrics and return a list of phonemes, extracted
        with a regular explression from the normalized lyrics fragment.

        >>> parse('test')
        [<Phoneme.T: 8>, <Phoneme.E: 2>, <Phoneme.S: 9>, <Phoneme.T: 8>]
        """
        if lyrics:
            if "\n" in lyrics and self.strict:
                raise ValueError("each note must contain at most one lyric")
            # Retrieve the first line of lyrics
            lyrics = lyrics.splitlines()[0]
            # Extract the lowercase text of each phoneme
            phonemes = [phoneme.name.lower() for phoneme in Phoneme]
            # Sort phonemes by length and build a regular expression
            expression = "|".join(sorted(phonemes, reverse=True, key=len))
            # Find and capture all the phonemes in the normalized text
            matches = re.findall(f"({expression})", self.normalize(lyrics))
            # Return a list of phoneme objects with all the matches
            return [Phoneme[match.upper()] for match in matches]
        else:
            return None

    def normalize(self, text: str) -> str:
        """Normalize text by converting them to lowercase, replacing non-ASCII
        characters by their normalized variants, and removing both punctuation
        and whitespace.

        >>> normalize("Té ;st")
        'test'
        """
        # Convert to lowercase
        text = text.casefold()
        # Normalize non-ASCII characters
        text = unicodedata.normalize("NFD", text)
        text = text.encode("ascii", "ignore").decode("utf-8")
        # Return only the alphabetic characters
        return re.sub("[^a-z]", "", text)
