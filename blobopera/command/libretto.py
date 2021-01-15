"""Inspect the default corpus of libretto texts."""
import requests
import typer

from ..libretto import Corpus
from ..phoneme import Phoneme
from . import common

application = typer.Typer()


@application.command()
def download(
    context: typer.Context,
    output: typer.FileBinaryWrite = typer.Argument(...),
    format: common.DownloadFormat = common.DefaultDownloadFormat,
):
    """Download the corpus of default recorded librettos from the server."""
    base: str = f"https://{context.obj.static}/blob-opera"
    address: str = f"{base}/recordedlibrettos.proto"
    content: bytes = requests.get(address).content

    if format is common.DownloadFormat.RAW:
        output.write(content)
    else:
        output.write(common.convert(content, format, message=Corpus))


@application.command()
def convert(
    input: typer.FileBinaryRead = typer.Argument(...),
    output: typer.FileBinaryWrite = typer.Argument(...),
    format: common.ConvertFormat = common.DefaultConvertFormat,
):
    """Convert a corpus of recorded librettos between internal formats."""
    output.write(common.convert(input.read(), format, message=Corpus))


@application.command()
def export(
    input: typer.FileBinaryRead = typer.Argument(...),
    output: typer.FileTextWrite = typer.Argument(...),
):
    """Export phonemes of recorded libretto in a human-friendly format."""
    corpus: Corpus = common.parse(input.read(), Corpus)

    for fragment in corpus.fragments:
        hyphenated = " ".join(
            Phoneme(timed.phoneme).name for timed in fragment.phonemes
        ).replace(Phoneme.SILENCE.name, "-")
        print(hyphenated, file=output)
