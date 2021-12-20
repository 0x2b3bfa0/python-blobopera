# `blobopera`

Tool to download, upload, import, export and analyze Blob Opera data.

**Usage**:

```console
$ blobopera [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--public-host TEXT`: [default: artsandculture.google.com]
* `--private-host TEXT`: [default: cilex-aeiopera.uc.r.appspot.com]
* `--static-host TEXT`: [default: gacembed.withgoogle.com]
* `--shortener-host TEXT`: [default: g.co]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `jitter`: Inspect the default set of audio jitter...
* `libretto`: Inspect the default corpus of libretto texts.
* `recording`: Operate with recording files and scores.

## `blobopera jitter`

Inspect the default set of audio jitter templates.

**Usage**:

```console
$ blobopera jitter [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `convert`: Convert a file with jitter templates between...
* `download`: Download the default file with jitter...
* `generate`: Generate pseudorandom jitters from a file...

### `blobopera jitter convert`

Convert a file with jitter templates between internal formats.

**Usage**:

```console
$ blobopera jitter convert [OPTIONS] INPUT OUTPUT
```

**Arguments**:

* `INPUT`: [required]
* `OUTPUT`: [required]

**Options**:

* `--format [JSON|BINARY]`: [required]
* `--help`: Show this message and exit.

### `blobopera jitter download`

Download the default file with jitter templates from the server.

**Usage**:

```console
$ blobopera jitter download [OPTIONS] OUTPUT
```

**Arguments**:

* `OUTPUT`: [required]

**Options**:

* `--format [JSON|BINARY|RAW]`: [default: RAW]
* `--help`: Show this message and exit.

### `blobopera jitter generate`

Generate pseudorandom jitters from a file with jitter templates.

**Usage**:

```console
$ blobopera jitter generate [OPTIONS] INPUT OUTPUT
```

**Arguments**:

* `INPUT`: [required]
* `OUTPUT`: [required]

**Options**:

* `--count INTEGER RANGE`
* `--seed INTEGER`
* `--help`: Show this message and exit.

## `blobopera libretto`

Inspect the default corpus of libretto texts.

**Usage**:

```console
$ blobopera libretto [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `convert`: Convert a corpus of recorded librettos...
* `download`: Download the corpus of default recorded...
* `export`: Export phonemes of recorded libretto in a...

### `blobopera libretto convert`

Convert a corpus of recorded librettos between internal formats.

**Usage**:

```console
$ blobopera libretto convert [OPTIONS] INPUT OUTPUT
```

**Arguments**:

* `INPUT`: [required]
* `OUTPUT`: [required]

**Options**:

* `--format [JSON|BINARY]`: [required]
* `--help`: Show this message and exit.

### `blobopera libretto download`

Download the corpus of default recorded librettos from the server.

**Usage**:

```console
$ blobopera libretto download [OPTIONS] OUTPUT
```

**Arguments**:

* `OUTPUT`: [required]

**Options**:

* `--format [JSON|BINARY|RAW]`: [default: RAW]
* `--help`: Show this message and exit.

### `blobopera libretto export`

Export phonemes of recorded libretto in a human-friendly format.

**Usage**:

```console
$ blobopera libretto export [OPTIONS] INPUT OUTPUT
```

**Arguments**:

* `INPUT`: [required]
* `OUTPUT`: [required]

**Options**:

* `--help`: Show this message and exit.

## `blobopera recording`

Operate with recording files and scores.

**Usage**:

```console
$ blobopera recording [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `convert`: Convert a recording file between internal...
* `download`: Download a recording file from the server.
* `export`: Export a recording to a musical score file.
* `import`: Import a recording from a musical score file.
* `upload`: Upload a recording file to the server.

### `blobopera recording convert`

Convert a recording file between internal formats.

**Usage**:

```console
$ blobopera recording convert [OPTIONS] INPUT OUTPUT
```

**Arguments**:

* `INPUT`: [required]
* `OUTPUT`: [required]

**Options**:

* `--format [JSON|BINARY]`: [required]
* `--help`: Show this message and exit.

### `blobopera recording download`

Download a recording file from the server.

This command tries to download a recording file from the server with
the given handle, be it a recording identifier, a link or a short link.

**Usage**:

```console
$ blobopera recording download [OPTIONS] HANDLE OUTPUT
```

**Arguments**:

* `HANDLE`: [required]
* `OUTPUT`: [required]

**Options**:

* `--format [JSON|BINARY|RAW]`: [default: RAW]
* `--help`: Show this message and exit.

### `blobopera recording export`

Export a recording to a musical score file.

This command tries to recreate a musical score from a given recording file,
converting phonemes to lyrics whenever possible (not supported for the
MIDI format) and mapping times and pitches to actual notes and rests.

**Usage**:

```console
$ blobopera recording export [OPTIONS] INPUT OUTPUT
```

**Arguments**:

* `INPUT`: [required]
* `OUTPUT`: [required]

**Options**:

* `--format [MUSICXML|MIDI|RAW]`: [default: MUSICXML]
* `--help`: Show this message and exit.

### `blobopera recording import`

Import a recording from a musical score file.

This command tries to create a recording file from a musical score,
resorting to the provided options to adjust the result.

Options:
    Theme: the festive theme adds fluffy red and white hats to singers
    and shows a falling snow animation through the entire scene.

    Format: the output format used for the recording file.

    Language: this language will be used to interpret the score lyrics and
    calculate the most accurate phonemes for each syllable; the random
    language builds random syllables from vowel + consonant pairs for
    every note.

    Default: a phoneme used to fill parts that don't have lyrics at all;
    silence will mute the affected voices, and any other value will
    make them sing a single vowel with the note pitches.

    Parts: for pieces with a number of parts other than four, these
    options will define which parts are used for which voices; 0 means
    the first (topmost) part, 1 the second, -1 the last, -2 the
    penultimate, et cetera.

    Tempo: this value modifies the global tempo by the specified amount;
    0.5 would slow down the piece to half its original speed, and 2.0
    would make it twice as quicker.

**Usage**:

```console
$ blobopera recording import [OPTIONS] INPUT OUTPUT
```

**Arguments**:

* `INPUT`: [required]
* `OUTPUT`: [required]

**Options**:

* `--format [BINARY|JSON]`: [default: BINARY]
* `--theme [NORMAL|FESTIVE]`: [default: NORMAL]
* `--language [GENERIC|RANDOM]`: [default: GENERIC]
* `--fill [SILENCE|A|E|I|O|U]`: [default: SILENCE]
* `--soprano-part INTEGER`: [default: 0]
* `--alto-part INTEGER`: [default: 1]
* `--tenor-part INTEGER`: [default: -2]
* `--bass-part INTEGER`: [default: -1]
* `--tempo FLOAT`: [default: 1.0]
* `--help`: Show this message and exit.

### `blobopera recording upload`

Upload a recording file to the server.

This command tries to upload the given recording file to the server and
return its handle in one of these variants:

IDENTIFIER: displays the raw recording identifier as
returned by the server.

LINK: displays a full link to the recording player, including the encoded
recording identifier as a parameter.

SHORT: displays a shortened version of the aforementioned link.

**Usage**:

```console
$ blobopera recording upload [OPTIONS] INPUT
```

**Arguments**:

* `INPUT`: [required]

**Options**:

* `--handle [IDENTIFIER|LINK|SHORT]`: [default: SHORT]
* `--help`: Show this message and exit.
