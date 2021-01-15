"""Main entry point when running through ``python -m``."""

from . import command

command.application(prog_name=__name__.split(".")[0])
