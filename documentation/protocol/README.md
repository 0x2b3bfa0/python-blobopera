# Protocol Buffers

This directory contains the protocol buffers used for internal
message serialization. These files were manually reverse-engineered
from the original application and have been preserved for documentation
purposes.

### Messages

* **`RecordingMessage`** describes a recording, including MIDI pitches, timing
  information and phonemes.

* **`RecordedLibrettos`** describes a list of predefined [librettos][1] that
  is being used during user-driven recordings; samples have been taken from
  actual Italian librettos —apparently [Nabucco][2].

* **`JitterTemplates`** describes a list of floating point templates that are
  being used to calculate pseudorandom audio jitter values.

### Enumerations

* **`Phoneme`** contains a list of valid [phonemes][3], including
  both vowels and consonants.

* **`Theme`** contains a list of valid themes; the festive theme adds
  falling snow and a red fluffy hat for each blob.

* **`Location`** contains a list of valid locations; i.e. blurry background
  pictures of emblematic places.

## Usage

```bash
protoc --decode RecordingMessage ./*/*.proto < recording.proto
protoc --decode JitterTemplates ./*/*.proto < jittertemplates.proto
protoc --decode RecordedLibrettos ./*/*.proto < recordedlibrettos.proto
```

[1]: https://en.wikipedia.org/wiki/Libretto
[2]: https://en.wikipedia.org/wiki/Nabucco
[3]: https://en.wikipedia.org/wiki/Phoneme
