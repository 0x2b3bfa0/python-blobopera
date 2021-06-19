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
    <a href="https://pypi.org/project/blobopera">
        <img alt="package" src="https://badge.fury.io/py/blobopera.svg">
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

## Documentation

* Full [command documentation][12].
* Generated [module documentation][19].

## Samples

* **[Adeste Fideles][5]** ([_source_][7], [_information_][6])
* **[Symphony No. 9 (Beethoven)][13]** ([_source_][15], [_information_][14])
* **[Ave Maria (Schubert)][20]** ([_source_][21], [_information_][22])
* **[O Magnum Mysterium (Brian Schmidt)][25]** ([_contributed sample_][26])
* **[Ave Verum Corpus (Mozart)][27]** ([_contributed sample_][28])
* **[Cum Sancto Spiritu - Gloria (Vivaldi)][29]** ([_contributed sample_][30])


:book:&nbsp;&nbsp;**Want to contribute a new sample? Click [here][24]!**

## Usage

1. Create a score file:
   Use [MuseScore][3] or similar to create a four-part score
   (soprano, alto, tenor and bass) with a single line of lyrics and export it
   to [MusicXML][4]. You can download MusicXML files from MuseScore
   by using [this tool][8].

2. Install the tool:
   ```bash
   pip install blobopera
   ```

3. Convert the score file:
   ```bash
   blobopera recording import input.musicxml output.binary
   ```
   _[(Take a look at the command-line options)][23]_

4. Upload the recording:
   ```bash
   blobopera recording upload output.binary
   ```

5. Visit the generated link with your browser.

## Roadmap

* [X] Publish the package.
* [ ] Add language-specific phoneme translators.
* [ ] Improve the phoneme relocation logic.
* [ ] Write granular unit tests.
* [ ] Extend the documentation.

## Contributing

1. Clone this repository:
   ```console
   $ git clone https://github.com/0x2b3bfa0/python-blobopera
   $ cd python-blobopera
   ```

2. Install the dependencies with [poetry][11]:
   ```console
   $ poetry install
   ```

4. Run the command-line tool:
   ```console
   $ poetry run blobopera
   ```

3. Run the module tests:
   ```console
   $ poetry run poe all
   ```

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
[13]: https://g.co/arts/vFxPVuuTATXNvX9F8
[14]: https://en.wikipedia.org/wiki/Symphony_No._9_(Beethoven)#IV._Finale
[15]: https://musescore.com/user/34418260/scores/6430537
[16]: https://artsandculture.google.com/experiment/blob-opera/AAHWrq360NcGbw?cp=eyJyIjoiNVNxb0RhRlB1VnRuIn0.
[17]: https://en.wikipedia.org/wiki/Mateo_Flecha
[18]: https://musescore.com/user/28092/scores/85307
[19]: https://0x2b3bfa0.github.io/python-blobopera
[20]: https://g.co/arts/xQGR5aWBwuDeGqTq8
[21]: http://www.cafe-puccini.dk/Schubert_GdurMesse.aspx
[22]: https://en.wikipedia.org/wiki/Ave_Maria_(Schubert)
[23]: ./documentation/command#blobopera-recording-import
[24]: https://github.com/0x2b3bfa0/python-blobopera/issues/new?labels=recording&template=new-recording.md&title=New+recording%3A+%7Btitle%7D
[25]: https://g.co/arts/8VGdX1SGjm2Tzyee7
[26]: https://github.com/0x2b3bfa0/python-blobopera/issues/4
[27]: https://g.co/arts/FqjgC2WJ6HyC2otv9
[28]: https://github.com/0x2b3bfa0/python-blobopera/issues/7
[29]: https://g.co/arts/77abQGtdkV72N3oW7
[30]: https://github.com/0x2b3bfa0/python-blobopera/issues/8
