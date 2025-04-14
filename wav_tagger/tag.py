from collections import namedtuple
from dataclasses import dataclass, asdict, field
import operator as op
from typing import List
from typing import NamedTuple
import os
import random

import ffmpeg

class WavMetadata(NamedTuple):
    title:  str
    artist: str
    album:  str
    track:  int
    genre:  str

@dataclass
class MetadataWriter:
    tmp_wav_fpath: str = field(init=False)
    tmp_metadata_fpath: str = field(init=False)

    def __post_init__(self):
        random_id = int(random.random()*(10**6))
        self.tmp_wav_fpath      = f'tmp_{random_id}.wav'
        self.tmp_metadata_fpath = f'tmp_{random_id}.txt'

    def write_to_wav(self, metadata: WavMetadata, wav_fpath: str):
        '''
        This function writes metadata to a wav file using ffmpeg.
        - Uses ffmpeg to create a new wav file with the metadata.
        - Tidies up by removing the temporary files.
        '''
        self._write_metadata_file(metadata)
        (
            ffmpeg
                .input(wav_fpath)
                .output(self.tmp_wav_fpath, codec="copy", map_metadata="1", loglevel="quiet")
                .global_args("-i", self.tmp_metadata_fpath)
                .overwrite_output()
                .run()
        )
        os.remove(self.tmp_metadata_fpath)
        os.rename(self.tmp_wav_fpath, wav_fpath)

    def read_from_wav(self, wav_fpath: str) -> WavMetadata:
        'Reads all metadata fields from a wav file, and returns a WavMetadata object with the main ones.'
        return WavMetadata(*op.itemgetter(*WavMetadata._fields)(self._read_all_wav_metadata(wav_fpath)))

    def _read_all_wav_metadata(self, wav_fpath: str) -> dict:
        (
            ffmpeg
                .input(wav_fpath)
                .output(self.tmp_metadata_fpath, format="ffmetadata", loglevel="quiet")
                .overwrite_output()
                .run()
        )
        # read the file, strip each line, and split each line by '=' to get key-value pairs
        return dict(map(
            op.methodcaller('split', '='),
            open(self.tmp_metadata_fpath, 'rb').read().decode(errors='replace').strip().split("\n")[1:]
        ))

    def _write_metadata_file(self, metadata: WavMetadata):
        with open(self.tmp_metadata_fpath, 'w') as ostream:
            print(';FFMETADATA1', file=ostream)
            for k, v in metadata._asdict().items():
                print(f'{k}={v}', file=ostream)
                if k == 'track':
                    print(f'ITRK={v}', file=ostream)
