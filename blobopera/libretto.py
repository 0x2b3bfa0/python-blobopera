import proto

from .phoneme import Phoneme

__protobuf__ = proto.module(package=__name__)


class Timed(proto.Message):
    """Timed libretto phoneme with absolute times in seconds."""

    phoneme = proto.Field(Phoneme, number=1, optional=True, json_name="name")
    start = proto.Field(
        proto.FLOAT, number=2, optional=True, json_name="start"
    )
    end = proto.Field(proto.FLOAT, number=3, optional=True, json_name="end")


class Libretto(proto.Message):
    """Sequence of timed libretto phonemes."""

    phonemes = proto.RepeatedField(
        Timed, number=1, optional=True, json_name="notes"
    )


class Corpus(proto.Message):
    """Sequence of librettos."""

    librettos = proto.RepeatedField(
        Libretto, number=1, optional=True, json_name="librettos"
    )
