import re
from dataclasses import dataclass
from pathlib import Path

import pytest  # type: ignore
import responses  # type: ignore

from .fixture_data_directory import data_directory


@pytest.fixture()
def mocked_static_server(data_directory):
    """Fixture that provides a static server mock."""
    with responses.RequestsMock() as _responses:
        yield Static(_responses, data_directory)


@dataclass
class Static:
    """Static server mock."""

    mock: responses.RequestsMock
    static_directory: Path
    static_host: str = "static.example.com"

    def __post_init__(self):
        """Initialize the mock server."""
        self.mock.add_callback(
            self.mock.GET,
            re.compile(
                f"https?://{re.escape(self.static_host)}/blob-opera/.*"
            ),
            callback=self.static,
        )

    def static(self, request):
        """Serve a static file from the test data directory."""
        files = {
            "jittertemplates.proto": "jitter.raw",
            "recordedlibrettos.proto": "libretto.raw",
        }
        path = self.static_directory / files[request.url.split("/").pop()]
        if path.exists():
            with open(path, "rb") as file:
                return (200, {}, file.read())
        else:
            return (404, {}, "Not Found")
