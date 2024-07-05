#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import json
import os

from wav_tagger import bandcamp, tag

from pygments import lexers, formatters, styles, highlight

SERVER_LIST_URL = 'https://surfheaven.eu/servers'


def ppd(d, indent=None, style='material'):
    'pretty-prints a dictionary, used for simple logs'
    print(highlight(json.dumps(d, indent=indent), lexers.JsonLexer(), formatters.TerminalTrueColorFormatter(style=styles.get_style_by_name(style))).strip())


@dataclass
class BandcampTag:
    fpath: str
    genre: str
    is_single_track: bool = False

    def __post_init__(self):
        if self.fpath.endswith('.zip'):
            self.dirpath = bandcamp.unzip(self.fpath)
        else:
            self.is_single_track = True
            album, artist = bandcamp.parse_album_metadata_from_fname(self.fpath)
            self.dirpath = f'{artist}/{album}'
            os.makedirs(self.dirpath, exist_ok=True)
            os.rename(self.fpath, os.path.join(self.dirpath, os.path.basename(self.fpath)))

    def run(self):
        for root, _, fnames in os.walk(self.dirpath):
            for fname in fnames:
                if not fname.endswith('.wav'):
                    continue
                if self.is_single_track:
                    album, artist = bandcamp.parse_album_metadata_from_fname(fname)
                    track = '01'
                    title = album
                else:
                    album, artist, track, title = bandcamp.parse_track_metadata_from_fname(fname)
                metadata = tag.WAVMetadata(
                    album  = album,
                    artist = artist,
                    track  = track,
                    title  = title,
                    genre  = self.genre,
                )
                fpath = os.path.join(root, fname)
                ppd(metadata.__dict__ | {'fpath': fpath})
                metadata.write_to_file(fpath)


def run(fpath: str, store: str, genre: str):
    ppd({'fpath': fpath, 'store': store, 'genre': genre})
    if store == 'bandcamp':
        BandcampTag(fpath, genre).run()


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-fpath', type=str, required=True)
    argparser.add_argument('-store', type=str, choices=['bandcamp'])
    argparser.add_argument('-genre', type=str)

    return argparser.parse_args().__dict__

if __name__ == '__main__':
    run(**parse_args())
