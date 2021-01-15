"""Phonemes used to represent lyrics for singing voice synthesis.

Note:
    This phoneme collection seems to have been designed with Italian or
    Eclesiastical Latin in mind, so it's quite hard to describe certain sounds
    from other languages, like the German vowels ü, ö and ä.
"""
import proto  # type: ignore

__protobuf__ = proto.module(package=__name__)


class Phoneme(proto.Enum):
    """Lyrics phoneme.

    Note:
        The special value :py:attr:`SILENCE` indicates
        the total absence of sound.
    """

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

    def is_vowel(self) -> bool:
        """Determine if the phoneme is a vowel.

        Returns:
            Whether the phoneme is a vowel or not.
        """
        return self in (self.A, self.E, self.I, self.O, self.U)

    def is_silence(self) -> bool:
        """Determine if the phoneme is a silence.

        Returns:
            Whether the phoneme is a :py:attr:`SILENCE` or not.
        """
        return self == self.SILENCE

    def is_consonant(self) -> bool:
        """Determine if the phoneme is a consonant.

        Returns:
            Whether the phoneme is a consonant or not.
        """
        return not self.is_vowel() and not self.is_silence()
