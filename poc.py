#!/usr/bin/env python3
'''
usage: python3 poc.py <dirpath> <metadata.json>

metadata format:
{
    "album": "album name",
    "tracks": [
        {"track": "01", "title": "track 1", "artist": "artist 1", "genre": "genre 1"},
        {"track": "02", "title": "track 2", "artist": "artist 2", "genre": "genre 2"},
    ]
}
'''

import argparse
import os, json, glob, sys
from dataclasses import dataclass, asdict

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalTrueColorFormatter

from wav_tagger import bandcamp, tag

def ppd(d, indent=2):
    'pretty-prints a dict'
    print(highlight(
        code      = json.dumps(d, indent=indent),
        lexer     = JsonLexer(),
        formatter = TerminalTrueColorFormatter()
    ).strip())

@dataclass
class Stores:
    bandcamp: str = 'bandcamp'
    beatport: str = 'beatport'
    @classmethod
    def values(cls): return list(map(lambda x: x.name, cls.__dataclass_fields__.values()))

@dataclass
class TrackMetadata:
    artist: str
    title: str
    track: str
    genre: str

@dataclass
class AlbumMetadata:
    album: str
    tracks: list[TrackMetadata]

    @staticmethod
    def from_dict(d: dict):
        return AlbumMetadata(
            album  = d['album'],
            tracks = [TrackMetadata(**t) for t in d['tracks']],
        )

    def write(self, fpath: str):
        json.dump(asdict(self), open(fpath, 'w'), indent=2)

def detect_bandcamp(dirpath: str) -> bool:
    for rootdir, dirnames, fnames in os.walk(dirpath):
        for fname in fnames:
            if fname in ('cover.jpg', 'cover.png'):
                continue
            try:
                bandcamp.parse_metadata_from_fname(fname)
            except ValueError:
                return False
    return True

def sort_bandcamp_files(fpaths: str):
    sorted_fpaths = [None]*len(fpaths)

    for fpath in fpaths:
        fname = os.path.basename(fpath)
        album, metadata = bandcamp.parse_metadata_from_fname(fname)
        sorted_fpaths[int(metadata['track'])-1] = fpath

    return sorted_fpaths

def run_with_metadata(dirpath: str, metadata_fpath: str):
    metadata = json.load(open(metadata_fpath))

    print('loaded metadata')
    ppd(metadata)

    print('bandcamp?', detect_bandcamp(os.path.basename(dirpath)))

    if detect_bandcamp(os.path.basename(dirpath)):
        fpaths = sort_bandcamp_files(glob.glob(f'{dirpath}/*.wav'))
    else:
        fpaths = sorted(glob.glob(f'{dirpath}/*.wav'))

    for fpath, track in zip(fpaths, metadata['tracks']):
        metadata = {
            'artist': track['artist'],
            'title': track['title'],
            'album': metadata['album'],
            'genre': track['genre'],
            'ITRK': str(int(track['track'])),
        }
        print('='*50, fpath, sep='\n')
        ppd(metadata)
        input('correct?')
        tag.write_wav_metadata(fpath=fpath, metadata=metadata)

def create_bandcamp_metadata(dirpath: str, genre: str, ofpath: str) -> AlbumMetadata:
    tracks = []
    album = None

    for fpath in sort_bandcamp_files(glob.glob(f'{dirpath}/*.wav')):
        track_album, track_metadata = bandcamp.parse_metadata_from_fname(os.path.basename(fpath))
        if album is None:
            album = track_album
        else:
            assert album == track_album, f'album mismatch: {album} != {track_album}'
        tracks.append(track_metadata | {'genre': genre})

    metadata = AlbumMetadata.from_dict({
        'album': album,
        'tracks': tracks,
    })
    metadata.write(ofpath)
    return metadata


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-dirpath', type=str, required=True)
    argparser.add_argument('-metadata', type=str)
    argparser.add_argument('-store', type=str, choices=Stores.values())
    argparser.add_argument('-genre', type=str)
    args = argparser.parse_args().__dict__

    if not args['metadata']:
        if not all([args['genre'], args['store']]):
            argparser.error('-genre and -store are required if -metadata is not specified')
    return args

if __name__ == '__main__':
    args = parse_args()

    if not args['metadata']:
        match args['store']:
            case Stores.bandcamp:
                metadata = create_bandcamp_metadata(dirpath=args['dirpath'], genre=args['genre'], ofpath='metadata.json')
                ppd(asdict(metadata))
            case Stores.beatport:
                print('beatport needs to be implemented')
                sys.exit(1)

    choice = input('write metadata?')
    if choice.lower() in ('y', 'yes'):
        run_with_metadata(dirpath=args['dirpath'], metadata_fpath='metadata.json')

