import json
import sys

import click
import music21

from google.protobuf.json_format import MessageToDict, Parse, ParseError
from google.protobuf.message import EncodeError, DecodeError
from requests.exceptions import RequestException

from blob.backend import Backend
from blob.music import Score
from blob.themes import Theme
from blob.protocol import RecordingMessage, RecordedLibrettos, JitterTemplates


@click.group()
@click.option("--public-host", default=Backend().public)
@click.option("--internal-host", default=Backend().internal)
@click.option("--embed-host", default=Backend().embed)
@click.pass_context
def main(context, public_host, internal_host, embed_host):
    """Tool to download, convert and analyze recorded librettos."""
    context.obj = Backend(public_host, internal_host, embed_host)


@main.group()
def recording():
    """Create, upload, download and convert recordings."""
    pass


@recording.command("convert")
@click.argument("input", type=click.File("rb"))
@click.argument("output", type=click.File("wb"))
@click.option(
    "--format",
    required=True,
    type=click.Choice(["JSON", "BINARY"], case_sensitive=False),
)
def convert_recording(input, output, format):
    """Convert a recording between text and binary formats."""
    if type(input) is not bytes:
        input = input.read()
    recording = parse(input, RecordingMessage)
    if format == "JSON":
        result = json.dumps(MessageToDict(recording), indent=2).encode()
    elif format == "BINARY":
        result = recording.SerializeToString()
    output.write(result)


@recording.command()
@click.argument("input", type=click.File("rb"))
@click.option(
    "--handle",
    default="SHORT",
    type=click.Choice(["IDENTIFIER", "LINK", "SHORT"], case_sensitive=False),
)
@click.pass_obj
def upload(backend, input, handle):
    """Upload a recording to the server and return its handle."""
    recording = parse(input.read(), RecordingMessage)
    identifier = backend.upload(recording)
    if handle in ["IDENTIFIER"]:
        click.echo(identifier)
    elif handle in ["LINK"]:
        click.echo(backend.link(identifier))
    elif handle in ["SHORT"]:
        click.echo(backend.shorten(backend.link(identifier)))


@recording.command()
@click.argument("handle", type=str)
@click.argument("output", type=click.File("wb"))
@click.option(
    "--format",
    default="RAW",
    type=click.Choice(["JSON", "BINARY", "RAW"], case_sensitive=False),
)
@click.pass_obj
@click.pass_context
def download(context, backend, handle, output, format):
    """Download a recording from the server."""
    try:
        data = backend.download(handle)
    except KeyError:
        click.echo("Error: Invalid recording handle", err=True)
        sys.exit(1)
    else:
        if format == "RAW":
            output.write(data)
        else:
            context.invoke(
                convert_recording,
                input=data,
                output=output,
                format=format
            )


@recording.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.argument("output", type=click.File("wb"))
@click.option(
    "--format",
    default="BINARY",
    type=click.Choice(["JSON", "BINARY"], case_sensitive=False),
)
@click.option(
    "--theme",
    default="NORMAL",
    type=click.Choice(["NORMAL", "FESTIVE"], case_sensitive=False),
)
@click.option("--tempo", default=1.0, type=float)
@click.pass_obj
@click.pass_context
def create(context, backend, input, output, format, theme, tempo):
    """Create a recording from the given MusicXML file."""
    music = music21.converter.parse(input)
    data = json.dumps(Score(music, theme=Theme[theme], tempo=tempo).data())
    context.invoke(
        convert_recording,
        input=data.encode(),
        output=output,
        format=format
    )


@main.group()
def libretto():
    """Download and convert the default corpus of recorded librettos."""
    pass


@libretto.command("convert")
@click.argument("input", type=click.File("rb"))
@click.argument("output", type=click.File("wb"))
@click.option(
    "--format",
    required=True,
    type=click.Choice(["JSON", "BINARY"], case_sensitive=False),
)
def convert_libretto(input, output, format):
    """Convert corpi of recorded librettos between text and binary formats."""
    if type(input) is not bytes:
        input = input.read()
    recording = parse(input, RecordedLibrettos)
    if format == "JSON":
        result = json.dumps(MessageToDict(recording), indent=2).encode()
    elif format == "BINARY":
        result = recording.SerializeToString()


@libretto.command("hyphenate")
@click.argument("input", type=click.File("rb"))
@click.argument("output", type=click.File("w"))
def convert_libretto(input, output):
    """Hyphenate phonemes of recorded librettos in a readable format."""
    recording = parse(input.read(), RecordedLibrettos)
    result = "\n".join(
        "-".join(note["name"] for note in libretto["notes"])
        for libretto in MessageToDict(recording)["librettos"]
    )
    output.write(result)


@libretto.command()
@click.argument("output", type=click.File("wb"))
@click.option(
    "--format",
    default="RAW",
    type=click.Choice(["JSON", "BINARY", "RAW"], case_sensitive=False),
)
@click.pass_obj
@click.pass_context
def download(context, backend, output, format):
    """Download the corpus of default recorded librettos from the server."""
    data = backend.librettos()
    if format == "RAW":
        output.write(data)
    else:
        context.invoke(
            convert_libretto,
            input=data,
            output=output,
            format=format
        )


@main.group()
def jitter():
    """Download and convert the default set of audio jitter templates."""
    pass


@jitter.command("convert")
@click.argument("input", type=click.File("rb"))
@click.argument("output", type=click.File("wb"))
@click.option(
    "--format",
    required=True,
    type=click.Choice(["JSON", "BINARY"], case_sensitive=False),
)
def convert_jitter(input, output, format):
    """Convert jitter templates between text and binary formats."""
    if type(input) is not bytes:
        input = input.read()
    recording = parse(input, JitterTemplates)
    if format == "JSON":
        result = json.dumps(MessageToDict(recording), indent=2).encode()
    elif format == "BINARY":
        result = recording.SerializeToString()
    output.write(result)


@jitter.command()
@click.argument("output", type=click.File("wb"))
@click.option(
    "--format",
    default="RAW",
    type=click.Choice(["JSON", "BINARY", "RAW"], case_sensitive=False),
)
@click.pass_obj
@click.pass_context
def download(context, backend, output, format):
    """Download the default jitter templates from the server."""
    data = backend.librettos()
    if format == "RAW":
        output.write(data)
    else:
        context.invoke(
            convert_jitter,
            input=data,
            output=output,
            format=format
        )


def parse(data: bytes, message: type) -> "message":
    try:
        try:
            # Try to interpret the input data as a JSON object
            recording = Parse(data, message())
            recording.SerializeToString()
        except (ParseError, UnicodeDecodeError):
            # Try to interpret the input data as a protocol buffer
            recording = message().FromString(data)
            recording.SerializeToString()
    except (EncodeError, DecodeError):
        # Does not seem to be a valid recording message
        click.echo("Error: Invalid input file", err=True)
        sys.exit(1)
    else:
        return recording


if __name__ == "__main__":
    try:
        main()
    except RequestException as exception:
        click.echo(f"Error: {exception}", err=True)
        sys.exit(1)
