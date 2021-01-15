"""Language protocol.

This file describes a protocol for the interaction between the recording
importer and the different language classes.
"""
from abc import abstractmethod
from typing import List, Protocol

import music21  # type: ignore

from ..phoneme import Phoneme


class Language(Protocol):
    """Language protocol / abstract base class.

    Example:
        >>> class CustomLanguage(Language):
        >>>     ...
    """

    @abstractmethod
    def __init__(self, part: music21.stream.Part, *, strict: bool):
        """Initialize the language with the complete part stream.

        Note:
            With the complete stream, the parser can look around and take
            decisions based on the surrounding lyrics, like altering a phoneme
            based on the previous and next ones.

        Arguments:
            part: The whole part of the score.
            strict: If true, don't allow events with multiple lyrics.
        """

    @abstractmethod
    def parse(
        self, before: List[dict], current: dict, after: List[dict]
    ) -> List[Phoneme]:
        """Parse lyrics from the given event.

        Arguments:
            before: A list with all the previous events.
            current: The current event.
            after: A list with all the next events.

        Returns:
            A list of phonemes representing the lyrics for the current event.
        """
