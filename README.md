<h1 align="center">Blob Opera Toolkit</h1>

<p align="center">
    <a href="https://github.com/0x2b3bfa0/python-blobopera/actions">
        <img alt="test" src="https://github.com/0x2b3bfa0/python-blobopera/workflows/test/badge.svg?branch=main">
    </a>
    <a href="https://github.com/0x2b3bfa0/python-blobopera/actions">
        <img alt="lint" src="https://github.com/0x2b3bfa0/python-blobopera/workflows/lint/badge.svg?branch=main">
    </a>
    <a href="https://github.com/0x2b3bfa0/python-blobopera/actions">
        <img alt="lint" src="https://github.com/0x2b3bfa0/python-blobopera/workflows/coverage/badge.svg?branch=main">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0">
        <img alt="license" src="https://img.shields.io/badge/license-GPL3-blue.svg">
    </a>
    <a href="https://github.com/psf/black">
        <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
</p>

## Description

Unofficial toolkit to convert MusicXML files into [Blob Opera][1] scores with
real lyrics, loosely inspired by [OverlappingElvis/blob-opera-midi][2].

## Demonstration

You can listen :point_right:[**here**][5]:point_left: to a custom version
of [Adeste Fideles][6] with real lyrics, extracted from [this score][7]
without any modification.

## Usage

1. Create a score file:
   Use [MuseScore][3] or similar to create a four-part score
   (soprano, alto, tenor and bass) with a single line of lyrics and export it
   to [MusicXML][4]. You can download MusicXML files from MuseScore
   by using [this tool][8].

2. Install the requirements (using [poetry][11]):
   ```bash
   poetry install
   ```

3. Convert the score file:
   ```bash
   poetry run blobopera recording import input.musicxml output.binary
   ```

4. Upload the recording:
   ```bash
   poetry run blobopera recording upload output.binary
   ```

5. Visit the generated link with your browser.

> :book:  ***You can also read the full [command documentation][12]***

## Known issues

* Pronunciation is far from perfect and consonants may be too faint
  to articulate the supporting note; feel free to add more
  language-phoneme maps.

* Timing can go completely off if the source score has metronome marks on it
  because they are being interpreted only for the first of the four parts.
  Please delete all the tempo marks on the score and use the `--tempo` option
  within the `recording create` subcommand in order to modify the global tempo:
  0.5 will slow down the entire recording to half the original speed.

## Contributing

Contributions are welcome! Don't forget to run `poetry run poe all` to
validate your code before starting a pull request.

[1]: https://artsandculture.google.com/experiment/blob-opera/AAHWrq360NcGbw
[2]: https://github.com/OverlappingElvis/blob-opera-midi
[3]: https://musescore.org/en
[4]: https://en.wikipedia.org/wiki/MusicXML
[5]: https://g.co/arts/hrjRDrpL5G7LrjRx7
[6]: https://en.wikipedia.org/wiki/O_Come,_All_Ye_Faithful
[7]: https://musescore.com/user/29729/scores/416701
[8]: https://github.com/Xmader/musescore-downloader
[11]: https://python-poetry.org/docs/
[12]: ./documentation/command
