#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import json
import os

from wav_tagger import bandcamp, tag

from pygments import lexers, formatters, styles, highlight

def ppd(d, indent=None, style='material'):
    'pretty-prints a dictionary, used for simple logs'
    print(highlight(json.dumps(d, indent=indent), lexers.JsonLexer(), formatters.TerminalTrueColorFormatter(style=styles.get_style_by_name(style))).strip())

def slugify_fpath(name: str):
    return name.replace('/', ' - ').replace(':', '_')

@dataclass
class UserDefinedTag:
    fpath: str
    metadata: tag.WavMetadata

    def __post_init__(self):
        self.odirpath = os.path.join(slugify_fpath(self.metadata.artist), slugify_fpath(self.metadata.album))

    def run(self):
        os.makedirs(self.odirpath, exist_ok=True)
        ofpath = os.path.join(self.odirpath, slugify_fpath(os.path.basename(self.fpath)))
        os.rename(self.fpath, ofpath)

        ppd(self.metadata.__dict__ | {'fpath': self.fpath, 'ofpath': ofpath})
        self.metadata.write_to_file(ofpath)

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

    def ordered_fname(album, artist, track, title, ext='wav'):
        '''
        original: Icicle, SP-MC - 20 Years Of Shogun Audio - 13 Dreadnaught (Break Remix).wav
        ordered:  20 Years Of Shogun Audio - 13 - Icicle, SP-MC - Dreadnaught (Break Remix).wav
        '''
        return ' - '.join([album, track, artist, title]) + '.wav'

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
                metadata = tag.WavMetadata(
                    album  = album,
                    artist = artist,
                    track  = int(track),
                    title  = title,
                    genre  = self.genre,
                )
                orig_fpath = os.path.join(root, fname)
                fpath = os.path.join(root, BandcampTag.ordered_fname(album=album, artist=artist, track=track, title=title))
                os.rename(orig_fpath, fpath)

                ppd(metadata.__dict__ | {'fpath': fpath})
                metadata.write_to_file(fpath)


def run(fpath: str, store: str, genre: str, metadata: dict = None):
    ppd({'fpath': fpath, 'store': store, 'genre': genre})

    if metadata:
        UserDefinedTag(fpath, tag.WavMetadata(**metadata)).run()
    elif store == 'bandcamp':
        BandcampTag(fpath, genre).run()


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-fpath', type=str, required=True)
    argparser.add_argument('-metadata', type=json.loads, required=False)
    argparser.add_argument('-store', type=str, choices=['bandcamp'])
    argparser.add_argument('-genre', type=str)

    return argparser.parse_args().__dict__

if __name__ == '__main__':
    run(**parse_args())
