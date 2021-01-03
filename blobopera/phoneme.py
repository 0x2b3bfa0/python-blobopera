import abc

import proto

__protobuf__ = proto.module(package=__name__)


class Classifiable:
    """Mixin that allows phoneme classes to determine its category."""

    @abc.abstractmethod
    def get(self) -> proto.Enum:
        """Return the enumeration object."""

    def vowel(self) -> bool:
        """Determine if the phoneme is a vowel."""
        return self.get().name.lower() in "aeiou"

    def silence(self) -> bool:
        """Determine if the phoneme is a silence."""
        return self.get().name.lower() == "silence"

    def consonant(self) -> bool:
        """Determine if the phoneme is a consonant."""
        return not self.get().vowel() and not self.get().silence()


class Phoneme(Classifiable, proto.Enum):
    """Phoneme enumeration."""

    I = 0
    A = 1
    E = 2
    O = 3
    SILENCE = 4
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

    def get(self):
        return self


class Timed(Classifiable, proto.Message):
    """Timed phoneme, with duration in a yet unknown unit of time."""

    phoneme = proto.Field(Phoneme, number=1, optional=True, json_name="name")
    duration = proto.Field(
        proto.FLOAT, number=2, optional=True, json_name="duration"
    )

    def get(self):
        return self.phoneme
