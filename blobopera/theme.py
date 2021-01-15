"""Graphical user interface themes.

This module describes the themes that can be used in the Blob Opera application
user interface.
"""
import proto  # type: ignore

__protobuf__ = proto.module(package=__name__)


class Theme(proto.Enum):
    """Graphical user interface theme.

    Note:
        The :py:attr:`FESTIVE` theme adds lots of tiny falling snowflakes
        in the background and Santa Claus hats over the singers.
    """

    NORMAL = 0
    FESTIVE = 1
