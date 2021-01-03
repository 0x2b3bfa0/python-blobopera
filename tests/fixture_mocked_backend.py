import json
import re
import secrets
from dataclasses import dataclass

import pytest
import responses


@pytest.fixture()
def mocked_backend():
    with responses.RequestsMock() as _responses:
        yield Backend(_responses)


@dataclass
class Backend:
    """Backend mock."""

    mock: responses.RequestsMock
    public_host: str = "public.example.com"
    private_host: str = "private.example.com"
    shortener_host: str = "shortener.example.com"
    data_host: str = "data.example.com"

    def __post_init__(self):
        self.shortener = Shortener(
            self.public_host, self.shortener_host, self.mock
        )
        self.storage = Storage(self.private_host, self.data_host, self.mock)
        self.mock.add(
            self.mock.GET,
            re.compile(f"https?://{re.escape(self.public_host)}/experiment"),
            body="Found",
            status=200,
        )


class Shortener:
    """Link shortener backend mock."""

    def __init__(
        self, control_host: str, link_host: str, mock: responses.RequestsMock
    ):
        """Initialize the backend with a "responses" mock and host names."""
        self.mock: responses.RequestsMock = mock
        self.control_host: str = control_host
        self.link_host: str = link_host
        self.objects: dict = {}

        self.mock.add_callback(
            self.mock.GET,
            re.compile(
                f"https?://{re.escape(self.control_host)}/api/shortUrl"
            ),
            callback=self.shorten,
        )
        self.mock.add_callback(
            self.mock.GET,
            re.compile(f"https?://{re.escape(self.link_host)}/.*"),
            callback=self.expand,
        )

    def expand(self, request):
        """Expand a shortened link."""
        if request.url.replace("http://", "https://") in self.objects:
            return (301, {"Location": self.objects[request.url]}, None)
        else:
            return (404, {}, "Dynamic Link Not Found")

    def shorten(self, request):
        """Shorten a long link."""
        identifier = f"https://{self.link_host}/{secrets.token_hex(6)}"
        if request.params.get("destUrl"):
            self.objects[identifier] = request.params["destUrl"]
            return (200, {}, f'GARBAGE"{identifier}"GARBAGE')
        else:
            return (200, {}, "GARBAGE")


class Storage:
    """Object storage backend mock."""

    def __init__(
        self, dynamic_host: str, static_host: str, mock: responses.RequestsMock
    ):
        """Initialize the backend with a "responses" mock and host names."""
        self.mock: responses.RequestsMock = mock
        self.dynamic_host: str = dynamic_host
        self.static_host: str = static_host
        self.objects: dict = {}

        self.mock.add_callback(
            self.mock.PUT,
            re.compile(f"https?://{re.escape(dynamic_host)}/recording"),
            callback=self.store,
        )
        self.mock.add_callback(
            self.mock.GET,
            re.compile(f"https?://{re.escape(dynamic_host)}/recording/.*"),
            callback=self.resolve,
        )
        self.mock.add_callback(
            self.mock.GET,
            re.compile(f"https?://{re.escape(static_host)}/.*"),
            callback=self.retrieve,
        )

    def store(self, request):
        """Store a recording in the object store."""
        key: str = secrets.token_hex(6)
        self.objects[key] = request.body
        return (200, {}, json.dumps({"id": key}))

    def resolve(self, request):
        """Resolve a recording identifier and return its address."""
        if (identifier := request.url.split("/").pop()) in self.objects:
            address: str = f"https://{self.static_host}/recording/{identifier}"
            return (200, {}, json.dumps({"url": address}))
        else:
            return (404, {}, "Not Found")

    def retrieve(self, request):
        """Retrieve a recording from the object store."""
        if (identifier := request.url.split("/").pop()) in self.objects:
            return (200, {}, self.objects[identifier])
        else:
            return (404, {}, "Not Found")
