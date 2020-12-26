# Blob Opera Toolkit

Toolkit to convert MusicXML files into [Blob Opera][1] scores with real lyrics,
loosely inspired by [OverlappingElvis/blob-opera-midi][2].

## Demo

You can listen :point_right:[**here**][5]:point_left: to a custom version
of [Adeste Fideles][6] with real lyrics, extracted from [this score][7]
without any modification.

## Known issues

* Pronunciation is far from perfect and consonants may be too faint
  to articulate the supporting note; feel free to add more language-phoneme maps.

* Timing is a bit off, and it can be worse if the source score has metronome
  marks on it, as they are being interpreted only for one of the four parts.
  Please delete all the tempo marks on the score and use the `--tempo` option
  within the `recording create` subcommand in order to modify the global tempo:
  0.5 will slow down the entire recording to half the original speed. 

## Usage

1. Create a score file:
   Use [MuseScore][3] or similar to create a four-part score
   (soprano, alto, tenor and bass) with a single line of lyrics and export it
   to [MusicXML][4]. You can download MusicXML files from MuseScore
   by using [this tool][8].

2. Install the requirements:
   ```bash
   pip install --requirement requirements.txt
   ```

3. Convert the score file:
   ```bash
   python blob.py recording create --theme=festive input.musicxml output.bin
   ```

4. Upload the recording:
   ```bash
   python blob.py recording upload output.bin
   ```

5. Visit the generated link with your browser.

### Downloading recordings

To download arbitrary recordings, just run the following command replacing `<handle>` with a recording identifier, a link or a short link:

```bash
python blob.py recording download --format=raw <handle> "example.bin"
```

Default carols have human-readable recording identifiers:

```bash
for carol in \
    "jinglebells" \
    "silentnight" \
    "joytotheworld" \
    "harktheheraldangelssing" \
    "awayinamanger" \
    "ocomeallyefaithful" \
    "thefirstnoel" \
    "onceinroyaldavidscity"
do
    python blob.py recording download --format=raw "$carol" "${carol}.bin"
done
```

### Inspecting recordings

```bash
python blob.py recording convert --format=json "example.bin" - | less
```

### Downloading librettos

```bash
python blob.py libretto download --format=raw "librettos.bin"
```

### Inspecting librettos

```bash
python blob.py libretto convert --format=json "librettos.bin" - | less
```

### Downloading jitter templates

```bash
python blob.py jitter download --format=raw "jitter.bin"
```

### Inspecting jitter templates

```bash
python blob.py jitter convert --format=json "jitter.bin" - | less
```

[1]: https://artsandculture.google.com/experiment/blob-opera/AAHWrq360NcGbw
[2]: https://github.com/OverlappingElvis/blob-opera-midi
[3]: https://musescore.org/en
[4]: https://en.wikipedia.org/wiki/MusicXML
[5]: https://g.co/arts/hrjRDrpL5G7LrjRx7
[6]: https://en.wikipedia.org/wiki/O_Come,_All_Ye_Faithful
[7]: https://musescore.com/user/29729/scores/416701
[8]: https://github.com/Xmader/musescore-downloader
[9]: https://developers.google.com/web/tools/chrome-devtools/open
[10]: https://developers.google.com/web/tools/chrome-devtools/javascript/breakpoints#loc
