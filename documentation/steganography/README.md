# Protocol Buffer Steganography

I started this project with the sole purpose of hiding some messages for a friend with some novel steganographic techniques, but I finally got carried away and chose to repurpose it for more general use cases, turning it into a full-fledged recording converter.

Technically, the idea behind protocol buffer steganography is very simple: the protocol buffer specification is flexible enough to accept unknown fields, and some servers don't remove those fields when storing uploaded messages, effectively allowing users to silently upload arbitrary data embedded into protocol buffer messages without introducing parse errors.

> [[...] messages created by your new code can be parsed by your old code: old binaries simply ignore the new field when parsing [...]](https://developers.google.com/protocol-buffers/docs/proto3#updating)
>  ***
> [Unknown fields are well-formed protocol buffer serialized data representing fields that the parser does not recognize. For example, when an old binary parses data sent by a new binary with new fields, those new fields become unknown fields in the old binary.](https://developers.google.com/protocol-buffers/docs/proto3#unknowns)

Users that are in the know can build an extended descriptor in order to retrieve the concealed information stored on the extraneous fields.

## Practical example

1. Alice has a server which accepts anonymous uploads of protocol buffer messages with the following descriptor:
    ```proto
    syntax = "proto2";

    message InconspicuousMessage {
      required string greeting = 1;
    }
    ```
    **Expected message example**
    ```
    00000000: 0a0d 4865 6c6c 6f2c 2077 6f72 6c64 21    ..Hello, world!
    ```
    
2. Bob uploads a crafted message, which includes a valid greeting along with a hidden string, by using the following descriptor:
    ```proto
    syntax = "proto2";

    message InconspicuousMessage {
      required string greeting = 1;
      required string hidden = 2;
    }
    ```
    **Crafted message example**
    ```
    00000000: 0a0d 4865 6c6c 6f2c 2077 6f72 6c64 2112  ..Hello, world!.
    00000010: 134a 6f68 616e 6e65 7320 5472 6974 6865  .Johannes Trithe
    00000020: 6d69 7573                                mius
    ```
    
3. Alice stores the uploaded message as-is on her public server because she's able to parse it without noticing any difference.
4. Charles downloads the message and parses it with the extended descriptor in order to recover the hidden text.

## Demonstration

```console
$ poetry run blobopera recording download https://g.co/arts/4NXntRPm8ut1ViL2A file.zip
$ unzip file.zip
Archive:  file.zip
 extracting: message.txt
$ cat message.txt
Johannes Trithemius
```
