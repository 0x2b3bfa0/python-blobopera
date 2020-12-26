# Protocol Buffers

This directory contains the protocol buffers used for internal
message serialization. Source files are being compiled automatically on import
through [`./code/__init__.py`][3], as performance is not an issue on this
use case.

### [Messages][1]

* **`RecordingMessage`** describes a recording, including MIDI pitches, timing
  information and phonemes.

* **`RecordedLibrettos`** describes a list of predefined [librettos][4] that
  is being used during user-driven recordings; samples have been taken from
  actual Italian librettos —apparently [Nabucco][6].

* **`JitterTemplates`** describes a list of floating point templates that are
  being used to calculate pseudorandom audio jitter values.

### [Enumerations][2]

* **`Phoneme`** contains a list of valid [phonemes][5], including
  both vowels and consonants.

* **`Theme`** contains a list of valid themes; the festive theme adds
  falling snow and a red fluffy hat for each blob.

## Usage

```bash
protoc --decode RecordingMessage */*.proto < recording.proto
protoc --decode JitterTemplates */*.proto < jittertemplates.proto
protoc --decode RecordedLibrettos */*.proto < recordedlibrettos.proto
```

[1]: ./messages
[2]: ./enumerations
[3]: ./code/__init__.py
[4]: https://en.wikipedia.org/wiki/Libretto
[5]: https://en.wikipedia.org/wiki/Phoneme
[6]: https://en.wikipedia.org/wiki/Nabucco
