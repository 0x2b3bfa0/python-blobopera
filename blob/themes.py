from enum import Enum


class Theme(Enum):
    """Interface themes; the festive theme adds red hats to blobs and
    renders some falling snow flakes through the scene.

    >>> Theme.FESTIVE
    <Theme.FESTIVE: 1>
    """

    DEFAULT = 0
    FESTIVE = 1
