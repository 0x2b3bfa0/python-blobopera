"""Tool to download, upload, import, export and analyze Blob Opera data."""

import typer

from ..backend import Backend
from . import jitter, libretto, recording


def main(
    context: typer.Context,
    public_host: str = Backend.public,
    private_host: str = Backend.private,
    static_host: str = Backend.static,
    shortener_host: str = Backend.shortener,
):
    """Initialize a backend instance to be shared amongst subcommands.

    Note:
        This function acts as the main application callback, and its only
        purpose is creating a singleton (more or less) backend object.
    """
    context.obj = Backend(
        public_host, private_host, static_host, shortener_host
    )


# Create the application with the documentation string and the main callback.
application = typer.Typer(help=__doc__.splitlines()[0], callback=main)


# Add each command to the main application.
for command in jitter, libretto, recording:
    application.add_typer(
        command.application,
        name=command.__name__.split(".")[-1],  # Last component.
        help=command.__doc__,  # Documentation string.
    )
