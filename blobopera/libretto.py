"""Corpus of libretto texts.

This module defines the protocol buffer format used for the default corpus of
libretto texts that is being used on interactive user-driven recordings. The
:py:class:`Corpus` class can be used to serialize and deserialize the
``recordedlibrettos.proto`` file from the original Blob Opera application.

Note:
    Texts on that file seem to come from Giuseppe Verdi's Otello, and serve as
    a good reference for translating Italian lyrics to phonemes with the
    :py:class:`Phoneme` syntax.
"""
import proto  # type: ignore

from .phoneme import Phoneme

__protobuf__ = proto.module(package=__name__)


class TimedPhoneme(proto.Message):
    """Timed libretto phoneme with absolute start and end times in seconds.

    Note:
        Not to be mistaken with :py:class:`.recording.TimedPhoneme`, which
        serves to a completely different purpose and has different fields.

    Attributes:
        phoneme (Phoneme): A :py:class:`Phoneme` object.
        start (float): The absolute start time, in seconds.
        end (float): The absolute end time, in seconds.
    """

    phoneme = proto.Field(Phoneme, number=1, optional=True, json_name="name")
    start = proto.Field(proto.FLOAT, number=2, optional=True)
    end = proto.Field(proto.FLOAT, number=3, optional=True)


class Fragment(proto.Message):
    """Libretto fragment containing phonemes for a few sentences.

    Attributes:
        phonemes (Sequence[TimedPhoneme]): A sequence of
            :py:class:`TimedPhoneme` objects.
    """

    phonemes = proto.RepeatedField(
        TimedPhoneme, number=1, optional=True, json_name="notes"
    )


class Corpus(proto.Message):
    """Corpus of default libretto fragments used for user-driven singing.

    Attributes:
        fragments (Sequence[Fragment]): A sequence of
            :py:class:`Fragment` objects.
    """

    fragments = proto.RepeatedField(
        Fragment, number=1, optional=True, json_name="librettos"
    )
