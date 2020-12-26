import base64
import json
import re

import requests

from .music import Score
from .protocol import RecordingMessage, RecordedLibrettos, JitterTemplates
from urllib.parse import urlparse, parse_qs


class Backend:
    def __init__(
        self,
        public: str = "artsandculture.google.com",
        internal: str = "cilex-aeiopera.uc.r.appspot.com",
        embed: str = "gacembed.withgoogle.com",
    ):
        """Initialize the backend with the public and private hosts."""
        self.internal = internal
        self.public = public
        self.embed = embed

    def shorten(self, link: str) -> str:
        """Shorten a link with the internal service."""
        address = f"https://{self.public}/api/shortUrl"
        response = requests.get(address, params={"destUrl": link})
        return re.search(r'.*"(https?://.+?)".*', response.text).group(1)

    def link(self, identifier: str) -> str:
        """Generate a link for a given recording identifier."""
        data = f'{{"r":"{identifier}"}}'.encode()
        # Encode the result with a custom Base64 URL-safe extended variant
        code = base64.urlsafe_b64encode(data).decode().replace("=", ".")
        # Return the link with the base prefix and the calculated identifier
        address = f"https://{self.public}/experiment/blob-opera/AAHWrq360NcGbw"
        return f"{address}?cp={code}"

    def publish(self, recording: RecordingMessage) -> str:
        """Publish a recording to the server and return its short link."""
        identifier = self.upload(recording)
        assert self.download(identifier) == recording
        return self.shorten(self.link(identifier))

    def upload(self, recording: RecordingMessage) -> str:
        """Upload a recording to the server and return its identifier."""
        data = recording.SerializeToString()
        address = f"https://{self.internal}/recording"
        response = requests.put(address, data=data)
        return response.json().get("id")

    def download(self, handle: str) -> bytes:
        """Download a recording from the server and return its contents."""
        try:
            if handle.startswith("https://g.co/arts/"):
                handle = requests.get(handle).url
            if handle.startswith(f"https://{self.public}"):
                code, *_ = parse_qs(urlparse(handle).query)["cp"]
                raw = base64.urlsafe_b64decode(code.replace(".", "="))
                handle = json.loads(raw)["r"]

            address = f"https://{self.internal}/recording/{handle}"
            file = requests.get(address).json()["url"]
            return requests.get(file).content

        except (json.decoder.JSONDecodeError, KeyError):
            raise KeyError("invalid recording handle")

    def librettos(self) -> bytes:
        """Download a list of recorded librettos from the server."""
        address = f"https://{self.embed}/blob-opera/recordedlibrettos.proto"
        return requests.get(address).content

    def templates(self) -> bytes:
        """Download a list of jitter templates from the server."""
        address = f"https://{self.embed}/blob-opera/jittertemplates.proto"
        return requests.get(address).content
