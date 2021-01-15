"""Common enumerations and functions.

This file provides data import functions and some shared defaults and
enumerations used by choice-like subcommand options.
"""
from enum import Enum
from typing import Type

import typer
from google.protobuf.json_format import ParseError
from google.protobuf.message import DecodeError, EncodeError
from proto import Message  # type: ignore


class ConvertFormat(str, Enum):
    JSON = "JSON"
    BINARY = "BINARY"


DefaultConvertFormat = typer.Option(..., case_sensitive=False)


class DownloadFormat(str, Enum):
    JSON = "JSON"
    BINARY = "BINARY"
    RAW = "RAW"


DefaultDownloadFormat = typer.Option(DownloadFormat.RAW, case_sensitive=False)


class ExportFormat(str, Enum):
    MUSICXML = "MUSICXML"
    MIDI = "MIDI"
    RAW = "RAW"


DefaultExportFormat = typer.Option(ExportFormat.MUSICXML, case_sensitive=False)


class ImportOutputFormat(str, Enum):
    BINARY = "BINARY"
    JSON = "JSON"


DefaultImportOutputFormat = typer.Option(
    ImportOutputFormat.BINARY, case_sensitive=False
)


class RecordingHandle(str, Enum):
    IDENTIFIER = "IDENTIFIER"
    LINK = "LINK"
    SHORT = "SHORT"


DefaultRecordingHandle = typer.Option(
    RecordingHandle.SHORT, case_sensitive=False
)


class PhonemeLanguage(str, Enum):
    GENERIC = "GENERIC"
    RANDOM = "RANDOM"


DefaultPhonemeLanguage = typer.Option(
    PhonemeLanguage.GENERIC, case_sensitive=False
)


class FillPhoneme(str, Enum):
    SILENCE = "SILENCE"
    A = "A"
    E = "E"
    I = "I"
    O = "O"
    U = "U"


DefaultFillPhoneme = typer.Option(FillPhoneme.SILENCE, case_sensitive=False)


class InterfaceTheme(str, Enum):
    NORMAL = "NORMAL"
    FESTIVE = "FESTIVE"


DefaultInterfaceTheme = typer.Option(
    InterfaceTheme.NORMAL, case_sensitive=False
)


def parse(data: bytes, message: Type[Message]) -> Message:
    """Parse a Protocol Buffer message from any of its representations.

    Arguments:
        data: the input data, either raw protocol buffer bytes or JSON bytes.
        message: the class (not an instance!) of the protocol buffer message.

    Returns:
        An instance of the given message type.
    """
    try:
        try:
            # Try to interpret the input data as a JSON object.
            result = message.from_json(data.decode())
            message.serialize(result)  # Sanity check.
        except (ParseError, UnicodeDecodeError):
            # Try to interpret the input data as a protocol buffer.
            result = message.deserialize(data)
            message.serialize(result)  # Sanity check.
    except (EncodeError, DecodeError):
        # Does not seem to be a valid recording message.
        typer.echo("Error: Invalid input file.", err=True)
        raise typer.Exit(code=1)
    else:
        return result


def convert(
    input: bytes, format: ConvertFormat, message: Type[Message]
) -> bytes:
    """Convert a Protocol Buffer message between its representations.

    Arguments:
        data: the input data, either raw protocol buffer bytes or JSON bytes.
        format: the output format for the conversion result.
        message: the class (not an instance!) of the protocol buffer message.

    Returns:
        The converted data.
    """

    structure = parse(input, message)
    if format == ConvertFormat.JSON:
        data: bytes = message.to_json(structure).encode()
    elif format == ConvertFormat.BINARY:
        data = message.serialize(structure)
    else:
        raise ValueError("invalid format")

    return data
