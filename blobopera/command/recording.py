"""Operate with recording files and scores."""
import tempfile
from pathlib import Path

import music21  # type: ignore
import typer

from ..languages import GenericLanguage, RandomLanguage
from ..phoneme import Phoneme
from ..recording import Recording
from ..theme import Theme
from . import common

application = typer.Typer()


@application.command()
def download(
    context: typer.Context,
    handle: str,
    output: typer.FileBinaryWrite = typer.Argument(...),
    format: common.DownloadFormat = common.DefaultDownloadFormat,
):
    """Download a recording file from the server.

    This command tries to download a recording file from the server with
    the given handle, be it a recording identifier, a link or a short link.
    """
    try:
        recording: bytes = context.obj.download(handle)  # Backend instance.
    except KeyError:
        typer.echo("Error: Invalid recording handle.", err=True)
        raise typer.Exit(code=1)
    else:
        if format is common.DownloadFormat.RAW:
            output.write(recording)
        else:
            output.write(common.convert(recording, format, message=Recording))


@application.command()
def upload(
    context: typer.Context,
    input: typer.FileBinaryRead = typer.Argument(...),
    handle: common.RecordingHandle = common.DefaultRecordingHandle,
):
    """Upload a recording file to the server.

    This command tries to upload the given recording file to the server and
    return its handle in one of these variants:

    IDENTIFIER: displays the raw recording identifier as
    returned by the server.

    LINK: displays a full link to the recording player, inluding the encoded
    recording identifier as a parameter.

    SHORT: displays a shortened version of the aforementioned link.
    """
    recording: Recording = common.parse(input.read(), Recording)
    data: bytes = Recording.serialize(recording)
    identifier: str = context.obj.upload(data)  # Backend instance.

    if handle == common.RecordingHandle.IDENTIFIER:
        typer.echo(identifier)
    elif handle == common.RecordingHandle.LINK:
        typer.echo(context.obj.link(identifier))
    elif handle == common.RecordingHandle.SHORT:
        typer.echo(context.obj.shorten(context.obj.link(identifier)))


@application.command()
def convert(
    input: typer.FileBinaryRead = typer.Argument(...),
    output: typer.FileBinaryWrite = typer.Argument(...),
    format: common.ConvertFormat = common.DefaultConvertFormat,
):
    """Convert a recording file between internal formats."""
    output.write(common.convert(input.read(), format, message=Recording))


@application.command("import")
def _import(  # Prepend an underscore because import is a reserved keyword.
    input: Path = typer.Argument(...),
    output: typer.FileBinaryWrite = typer.Argument(...),
    format: common.ImportOutputFormat = common.DefaultImportOutputFormat,
    theme: common.InterfaceTheme = common.DefaultInterfaceTheme,
    language: common.PhonemeLanguage = common.DefaultPhonemeLanguage,
    fill: common.FillPhoneme = common.DefaultFillPhoneme,
    soprano_part: int = 0,
    alto_part: int = 1,
    tenor_part: int = -2,
    bass_part: int = -1,
    tempo: float = 1.0,
):
    """Import a recording from a musical score file.

    This command tries to create a recording file from a musical score,
    resorting to the provided options to adjust the result.

    Options:
        Theme: the festive theme adds fluffy red and white hats to singers
        and shows a falling snow animation through the entire scene.

        Format: the output format used for the recording file.

        Language: this language will be used to interpret the score lyrics and
        calculate the most accurate phonemes for each syllable; the random
        language builds random syllables from vowel + consonant pairs for
        every note.

        Default: a phoneme used to fill parts that don't have lyrics at all;
        silence will mute the affected voices, and any other value will
        make them sing a single vowel with the note pitches.

        Parts: for pieces with a number of parts other than four, these
        options will define which parts are used for which voices; 0 means
        the first (topmost) part, 1 the second, -1 the last, -2 the
        penultimate, et cetera.

        Tempo: this value modifies the global tempo by the specified amount;
        0.5 would slow down the piece to half its original speed, and 2.0
        would make it twice as quicker.
    """

    if language == common.PhonemeLanguage.GENERIC:
        language = GenericLanguage
    if language == common.PhonemeLanguage.RANDOM:
        language = RandomLanguage

    score = music21.converter.parse(input)
    parts = soprano_part, alto_part, tenor_part, bass_part

    if len(score.parts) == 0:
        typer.echo("Error: no parts detected.", err=True)
        raise typer.Exit(code=1)
    elif len(score.parts) == 1:
        parts = (0, 0, 0, 0)  # Assign the same part to all the voices.

    recording = Recording.from_score(
        score=score,
        theme=Theme[theme.value],
        language=language,
        tempo=tempo,
        parts=parts,
        fill=Phoneme[fill.value],
    )

    output.write(
        common.convert(
            Recording.serialize(recording), format, message=Recording
        )
    )


@application.command()
def export(
    input: typer.FileBinaryRead = typer.Argument(...),
    output: typer.FileBinaryWrite = typer.Argument(...),
    format: common.ExportFormat = common.DefaultExportFormat,
):
    """Export a recording to a musical score file.

    This command tries to recreate a musical score from a given recording file,
    converting phonemes to lyrics whenever possible (not supported for the
    MIDI format) and mapping times and pitches to actual notes and rests.
    """
    stream = common.parse(input.read(), Recording).to_score()

    # Exports in music21 override file extensions and have erratic behavior.
    with tempfile.TemporaryDirectory() as directory:
        path = stream.write(format, fp=Path(directory) / "file")
        with open(path, "rb") as data:
            output.write(data.read())
