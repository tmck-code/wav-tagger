from dataclasses import dataclass
from typing import List
from collections import namedtuple
from itertools import count
import os

import ffmpeg

Metadata = namedtuple('metadata', ['key', 'value'])

FF_META = "out.txt"

@dataclass
class WAVMetadata:
    title: str = ''
    artist: str = ''
    album: str = ''
    track: int = 0
    genre: str = ''

    def _gen_metadata_args(self) -> dict:
        return {f"metadata:g:{i}": f"{k}={v}" for i,(k,v) in zip(count(), self.__dict__.items()) if v}

def parse_wav_metadata(wav_fpath: str):
    (
        ffmpeg
            .input(wav_fpath)
            .output(FF_META, format="ffmetadata", loglevel="quiet")
            .overwrite_output()
            .run()
    )
    data = open(FF_META, 'rb').read().decode(errors='replace').strip().split("\n")
    print(data)
    return dict([
        tuple(l.split("=", 1)) for l in data[3:]
    ])

def write_metadata_file(metadata: dict, fpath: str = FF_META):
    with open(fpath, "w") as ostream:
        ostream.write(";FFMETADATA1\n")
        ostream.write("\n".join("=".join([k,v]) for k,v in metadata.items()))

def write_metadata(metadata_fpath: str, fpath: str, ofpath: str):
    (
        ffmpeg
            .input(fpath)
            .output(ofpath, codec="copy", map_metadata="1", loglevel="quiet")
            .global_args("-i", metadata_fpath)
            .overwrite_output()
            .run()
    )

def write_wav_metadata(fpath: str, metadata: dict):
    tmp_fpath = 'tmp.wav'
    write_metadata_file(metadata, FF_META)
    write_metadata(FF_META, fpath, tmp_fpath)
    os.rename(tmp_fpath, fpath)
    os.remove(FF_META)

