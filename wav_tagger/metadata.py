from __future__ import annotations

from dataclasses import dataclass
import os

import ffmpeg

FF_META = "out.txt"

@dataclass
class Metadata:
    track: str
    title: str
    artist: str
    album: str
    encoder: str
    genre: str = ""

    FF_META_HEADER = ";FFMETADATA"

    @staticmethod
    def from_file(fpath) -> Metadata:
        raw = Metadata._probe_raw_ffmetadata(fpath).split("\n")
        header = raw[0]
        values = {}
        for line in raw[1:]:
            k, v = line.split("=")
            if k in Metadata.__dataclass_fields__.keys():
                values[k] = v
        return Metadata(**values)

    @staticmethod
    def _probe_raw_ffmetadata(fpath):
        (
            ffmpeg
                .input(fpath)
                .output(FF_META, format="ffmetadata", loglevel="quiet")
                .overwrite_output()
                .run()
        )
        data = open(FF_META, 'rb').read().decode(errors='replace').strip()
        os.remove(FF_META)
        return data

