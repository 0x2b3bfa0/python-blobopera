import music21  # type: ignore
import pytest  # type: ignore

from blobopera.languages import GenericLanguage, RandomLanguage
from blobopera.phoneme import Phoneme

from .fixture_note_lyric_events import foo_events, foo_none_events


def test_random_language(foo_none_events):
    language = RandomLanguage(music21.stream.Part(), strict=False)
    for event in foo_none_events:
        vowel, consonant = language.parse(*event)
        assert consonant.is_consonant()
        assert vowel.is_vowel()


def test_random_language_strict_fail(foo_events):
    language = RandomLanguage(music21.stream.Part(), strict=True)
    error = "random language doesn't accept lyrics"
    for event in foo_events:
        with pytest.raises(ValueError, match=error):
            language.parse(*event)
