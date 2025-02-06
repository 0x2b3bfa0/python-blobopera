import music21  # type: ignore
import pytest  # type: ignore

from blobopera.languages import GenericLanguage
from blobopera.phoneme import Phoneme

from .fixture_note_lyric_events import foo_events, none_events

def test_generic_language(foo_events):
    language = GenericLanguage(music21.stream.Part(), strict=False)
    for event in foo_events:
        phonemes = language.parse(*event)
        assert phonemes == [Phoneme.F, Phoneme.O, Phoneme.O]


def test_generic_language_strict_fail(foo_events):
    language = GenericLanguage(music21.stream.Part(), strict=True)
    error = "each note must contain at most one lyric"
    for event in foo_events:
        with pytest.raises(ValueError, match=error):
            language.parse(*event)


def test_generic_language_none(none_events):
    language = GenericLanguage(music21.stream.Part(), strict=True)
    for event in none_events:
        phonemes = language.parse(*event)
        assert isinstance(phonemes, list)
        assert not phonemes
