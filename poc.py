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


from wav_tagger import tag
import os, json, glob, sys

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalTrueColorFormatter

def ppd(d, indent=2):
    'pretty-prints a dict'
    print(highlight(
        code      = json.dumps(d, indent=indent),
        lexer     = JsonLexer(),
        formatter = TerminalTrueColorFormatter()
    ).strip())

def run(dirpath: str, metadata_fpath: str):
    metadata = json.load(open(metadata_fpath))

    print('loaded metadata')
    ppd(metadata)
    for i, (fpath, track) in enumerate(zip(sorted(glob.glob(f'{dirpath}/*.wav')), metadata['tracks'])):
        metadata = {
            'artist': track['artist'],
            'title': track['title'],
            'album': metadata['album'],
            'genre': track['genre'],
            'ITRK': str(int(track['track'])),
        }
        ppd(metadata)
        print(fpath)
        input('correct?')
        tag.write_wav_metadata(fpath=fpath, metadata=metadata)

def run_beatport():
    ifdir = sys.argv[1]

    paths = []
    for fpath in glob.glob(f"{ifdir}/*.wav"):
        print(fpath, end="", flush=True)
        md = grab_track_info(fpath.lstrip("./"))
        print(f" : {md}")
        paths.append((fpath, md))

    input("does this look right?")

    for fpath, md in paths:
        os.makedirs(f"./{md['artist']}/{md['album']}", exist_ok=True)
        write_metadata(fpath, md, f"./{md['artist']}/{md['album']}/{os.path.basename(fpath)}")

if __name__ == '__main__':
    run(dirpath=sys.argv[1], metadata_fpath=sys.argv[2])

