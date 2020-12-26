import re
import unicodedata

from typing import List, Optional

from .phonemes import Phoneme, Timed


class Syllable:
    """Syllable formed by one or more phonemes; usually a vowel
    followed by a suffix formed by one or more vowels and consonants.

    >>> Syllable([Phoneme.A, Phoneme.B, Phoneme.C])
    <Syllable object at ...>
    """

    def __init__(
        self, phonemes: Optional[List[Phoneme]] = None, *, strict: bool = True
    ):
        # Retrieve the vowel and the suffix or use silences as default values
        vowel, *suffix = phonemes or 2 * [Phoneme.SIL]

        # Check that vowel is a vowel
        if strict and vowel.consonant():
            raise ValueError("first phoneme of a syllable must be vowel")

        # Assign the timed values
        self.vowel: Timed = Timed(vowel, 0.1)
        self.suffix: List[Timed] = Suffix(suffix)

    def data(self) -> dict:
        return {"vowel": self.vowel.data(), "suffix": self.suffix.data()}


class Suffix:
    """Syllable suffix formed by one or more many phonemes; usually
    one or more consonants.

    >>> Suffix([Phoneme["T"], Phoneme["SH"]])
    <Suffix object at ...>
    """

    def __init__(
        self, phonemes: Optional[List[Phoneme]] = None, *, strict: bool = True
    ):
        # Retrieve the the suffix or use silence as default value
        suffix = phonemes or [Phoneme.SIL]

        # Check that every phoneme is a consonant
        if strict and any(phoneme.vowel() for phoneme in suffix):
            raise ValueError("phonemes of a suffix must be consonants")

        # Assign the timed values
        self.phonemes = [Timed(phoneme, 0.05) for phoneme in suffix]

    def data(self) -> dict:
        return [phoneme.data() for phoneme in self.phonemes]
