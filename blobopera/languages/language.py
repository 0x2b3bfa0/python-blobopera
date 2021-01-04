from abc import abstractmethod
from typing import List, Optional, Protocol

import music21

from ..phoneme import Phoneme


class Language(Protocol):
    @abstractmethod
    def __init__(self, part: music21.stream.Part):
        pass

    @abstractmethod
    def parse(
        self, time: float, lyrics: Optional[str], index: int
    ) -> Optional[List[Phoneme]]:
        pass
