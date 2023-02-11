"""Graphical user interface locations.

This module describes the location pictures that can be used in
the Blob Opera application user interface.
"""
import proto  # type: ignore

__protobuf__ = proto.module(package=__name__)


class Location(proto.Enum):
    """Background picture for the Blob Opera stage.

    Note:
        BlobperaHouse is a generic background.
        Others are blurry outdoor views of emblematic places.
    """

    BLOBPERAHOUSE = 0
    LONDON = 1
    NEWYORK = 2
    HACKNEY = 3
    PARIS = 4
    CAPETOWN = 5
    MEXICOCITY = 6
    SEOUL = 7
