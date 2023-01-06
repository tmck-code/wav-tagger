# wav-tagger
A utility to tag .wav tunes, backed by ffmpeg

## WAV Metadata

### LIST Metadata

This format is the most basic available

It essentially has 5 fields that are readable by music players

- INAM / title
- IART / artist
- IPRD / album
- IGNR / genre
- ICMT / comment

The ffmpeg tool actually supports writing some others, but these aren't
recognised/read on the music players I've tested so far

> `https://wiki.multimedia.cx/index.php/FFmpeg_Metadata`

(see the "AVI" section")
```
"IARL"
"IART", "artist"
"ICMS"
"ICMT", "comment"
"ICOP", "copyright"
"ICRD", "date"
"ICRP"
"IDIM"
"IDPI"
"IENG"
"IGNR", "genre"
"IKEY"
"ILGT"
"ILNG", "language"
"IMED"
"INAM", "title"
"IPLT"
"IPRD", "album"
"IPRT", "track"
"ISBJ"
"ISFT", "encoder" - note that this is automatically filled in by libavformat
"ISHP"
"ISRC"
"ISRF"
"ITCH", "encoded_by"
```

