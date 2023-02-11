"""Graphical user interface themes.

This module describes the themes that can be used in the Blob Opera application
user interface.
"""
import proto  # type: ignore

__protobuf__ = proto.module(package=__name__)


class Theme(proto.Enum):
    """Graphical user interface theme.

    Note:
        The :py:attr:`CHRISTMAS` theme adds lots of tiny falling snowflakes
        in the background and Santa Claus hats over the singers.

        The :py:attr:`NEWYEARS` theme adds lots of tiny falling snowflakes
        in the background, party hats over the singers and a big aluminum
        balloon with the year on it hovering their heads.
    """

    NORMAL = 0
    CHRISTMAS = 1
    NEWYEARS = 2
