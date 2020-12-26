from dataclasses import dataclass
from enum import Enum


class Phoneme(Enum):
    I = 0
    A = 1
    E = 2
    O = 3
    SIL = 4
    R = 5
    N = 6
    L = 7
    T = 8
    S = 9
    D = 10
    U = 11
    M = 12
    P = 13
    V = 14
    CH = 15
    C = 16
    F = 17
    J = 18
    B = 19
    H = 20
    G = 21
    QU = 22
    SH = 23
    NY = 24
    Y = 25
    SK = 26
    Z = 27
    TZ = 28

    def vowel(self) -> bool:
        return self.name.lower() in "aeiou"

    def silence(self) -> bool:
        return self.name.lower() == "sil"

    def consonant(self) -> bool:
        return not self.vowel() and not self.silence()


@dataclass
class Timed:
    phoneme: Phoneme
    duration: float

    # Base functions
    vowel = Phoneme.vowel
    silence = Phoneme.silence
    consonant = Phoneme.consonant

    def __post_init__(self):
        self.name = self.phoneme.name
        self.value = self.phoneme.value

    def data(self) -> dict:
        return {"name": self.value, "duration": self.duration}
