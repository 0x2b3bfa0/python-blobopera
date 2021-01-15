import pytest  # type: ignore
from typer.testing import CliRunner

from blobopera import command


@pytest.fixture()
def invoke_command():
    """Fixture that provides a command-line interface
    runner to invoke the main Typer application command.
    """
    runner = CliRunner()

    def partial(*arguments):
        return runner.invoke(command.application, [*map(str, arguments)])

    return partial
