import base64
import json
import re
import urllib.parse
from dataclasses import dataclass

import requests


@dataclass
class Backend:
    public: str = "artsandculture.google.com"
    private: str = "cilex-aeiopera.uc.r.appspot.com"
    static: str = "gacembed.withgoogle.com"
    shortener: str = "g.co"

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

    def upload(self, recording: bytes) -> str:
        """Upload a recording to the server and return its identifier."""

        address = f"https://{self.private}/recording"
        response = requests.put(address, data=recording)

        try:
            return response.json()["id"]
        except (json.decoder.JSONDecodeError, KeyError):
            raise ValueError("invalid recording")

    def download(self, handle: str) -> bytes:
        """Download a recording from the server and return its contents."""
        try:
            if handle.startswith(f"https://{self.shortener}"):
                handle = requests.get(handle).url
            if handle.startswith(f"https://{self.public}"):
                code, *_ = urllib.parse.parse_qs(
                    urllib.parse.urlparse(handle).query
                )["cp"]
                raw = base64.urlsafe_b64decode(code.replace(".", "="))
                handle = json.loads(raw)["r"]

            address = f"https://{self.private}/recording/{handle}"
            file = requests.get(address).json()["url"]
            return requests.get(file).content

        except (json.decoder.JSONDecodeError, KeyError):
            raise KeyError("invalid recording handle")
