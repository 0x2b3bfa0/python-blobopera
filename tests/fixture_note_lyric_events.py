import more_itertools
import music21  # type: ignore
import pytest  # type: ignore


def generate_windowed_events(lyrics: list):
    """Generate windowed events to feed a language parser.

    Yields event tuples with all the previous elements, the current element
    and all the next elem. in the form ((..., previous), current, (next, ...)).
    """
    # FIXME: https://github.com/cuthbertLab/music21/pull/769 pending.
    # notes = [music21.note.Note(lyric=lyric) for lyric in lyrics]  # noqa E800
    notes = [
        music21.note.Note()
        if lyric is None
        else music21.note.Note(lyric=lyric)
        for lyric in lyrics
    ]
    for before, current, after in more_itertools.windowed_complete(notes, 1):
        yield before, current[0], after


@pytest.fixture()
def foo_none_events():
    """Fixture that provides note events with lyrics (alternating)."""
    return generate_windowed_events(["Fö; o\n.", None] * 10)


@pytest.fixture()
def foo_events():
    """Fixture that provides note events with lyrics (foo unicode)."""
    return generate_windowed_events(["Fö; o\n."] * 10)


@pytest.fixture()
def none_events():
    """Fixture that provides note events with lyrics (none)."""
    return generate_windowed_events([None] * 10)
