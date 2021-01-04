"""Inspect the default set of audio jitter templates."""

from itertools import islice
from typing import Optional

import requests
import typer

from ..jitter import Generator, Jitter
from . import common

application = typer.Typer()


@application.command()
def download(
    context: typer.Context,
    output: typer.FileBinaryWrite = typer.Argument(...),
    format: common.DownloadFormat = common.DefaultDownloadFormat,
):
    """Download the default file with jitter templates from the server."""
    base: str = f"https://{context.obj.static}/blob-opera"
    address: str = f"{base}/jittertemplates.proto"
    content: bytes = requests.get(address).content

    if format is common.DownloadFormat.RAW:
        output.write(content)
    else:
        output.write(common.convert(content, format, message=Jitter))


@application.command()
def convert(
    input: typer.FileBinaryRead = typer.Argument(...),
    output: typer.FileBinaryWrite = typer.Argument(...),
    format: common.ConvertFormat = common.DefaultConvertFormat,
):
    """Convert a file with jitter templates between internal formats."""
    output.write(common.convert(input.read(), format, message=Jitter))


@application.command()
def generate(
    input: typer.FileBinaryRead = typer.Argument(...),
    output: typer.FileTextWrite = typer.Argument(...),
    count: Optional[int] = typer.Option(None, min=1),
    seed: Optional[int] = None,
):
    """Generate pseudorandom jitters from a file with jitter templates."""
    jitter: Jitter = common.parse(input.read(), Jitter)
    generator: Generator = Generator(jitter, seed=seed)

    for value in islice(generator, count):
        print(value, file=output)
