import base64
import json
import re
import urllib.parse
from dataclasses import dataclass

import requests


@dataclass
class Backend:
    """Interface for interacting directly with the server backend.

    Arguments:
        public: The host name of the public server.
        private: The host name of the private server.
        static: The host name of the static server.
        shortener: The host name of the link shortener server.
    """

    public: str = "artsandculture.google.com"
    private: str = "cilex-aeiopera.uc.r.appspot.com"
    static: str = "gacembed.withgoogle.com"
    shortener: str = "g.co"

    def shorten(self, link: str) -> str:
        """Shorten a link with the internal shortener service.

        Arguments:
            link: The link to shorten.

        Returns:
            A shortened link from g.co

        Raises:
            KeyError: If the shortener did not reply with a link.
        """
        address = f"https://{self.public}/api/shortUrl"
        response = requests.get(address, params={"destUrl": link})
        # We can't parse the response as JSON because it includes garbage.
        if match := re.search(r'.*"(https?://.+?)".*', response.text):
            return match.group(1)
        else:
            raise KeyError("no link found")

    def link(self, identifier: str) -> str:
        """Generate a link for the given recording identifier.

        Arguments:
            identifier: The recording identifier in Base64.

        Returns:
            A long link pointing to the recording on the main Blob Opera page.
        """
        # Generate the indentifier bytes.
        data = f'{{"r":"{identifier}"}}'.encode()
        # Encode the result with a custom Base64 URL-safe extended variant.
        code = base64.urlsafe_b64encode(data).decode().replace("=", ".")
        # Return the link with the base prefix and the calculated identifier.
        address = f"https://{self.public}/experiment/blob-opera/AAHWrq360NcGbw"
        return f"{address}?cp={code}"

    def upload(self, recording: bytes) -> str:
        """Upload the given recording to the server and return its identifier.

        Arguments:
            recording: The recording, serialized with its protocol buffer.

        Returns:
            A recording identifier.

        Raises:
            ValueError: If the uploaded recording was rejected by the server.
        """

        address = f"https://{self.private}/recording"
        response = requests.put(address, data=recording)

        try:
            return response.json()["id"]
        except (json.decoder.JSONDecodeError, KeyError):
            raise ValueError("invalid recording")

    def download(self, handle: str) -> bytes:
        """Download a recording from the server and return its contents.

        Arguments:
            handle: The recording handle, be it a short link, a long link or
                a recording identifier.

        Returns:
            A raw protocol buffer message with the recording.

        Raises:
            KeyError: If the recording was not found on the server.
        """
        try:
            # If it's a short link, try to resolve the long link.
            if handle.startswith(f"https://{self.shortener}"):
                handle = requests.get(handle).url

            # If it's a long link, try to retrieve the identifier.
            if handle.startswith(f"https://{self.public}"):
                # Extract the query string from the address.
                query_string = urllib.parse.urlparse(handle).query
                # Extract the ``cp`` parameter from the query string.
                code, *_ = urllib.parse.parse_qs(query_string)["cp"]
                # Decode the ``cp`` parameter with the custom url-safe Base64.
                raw = base64.urlsafe_b64decode(code.replace(".", "="))
                # Extract the recording identifier.
                handle = json.loads(raw)["r"]

            # Fetch the recording and return the raw protocol buffer.
            address = f"https://{self.private}/recording/{handle}"
            file = requests.get(address).json()["url"]
            return requests.get(file).content

        except (json.decoder.JSONDecodeError, KeyError):
            raise KeyError("invalid recording handle")
