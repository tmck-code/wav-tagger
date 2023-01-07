#!/usr/bin/env python3

from wav_tagger import tag
import os, json, glob, sys

dirpath = sys.argv[1]

for fpath in glob.glob(f'{dirpath}/*.wav'):
    artist, album, remainder = os.path.splitext(os.path.basename(fpath))[0].split(' - ', 2)
    print(f'{artist=}, {album=}, {remainder=}')
    track_number, title = remainder.strip().split(' ', 1)
    print(f'{track_number=}, {title=}')
    metadata = {
        'artist': artist,
        'title': title,
        'album': album,
        'track': str(int(track_number)),
        'ITRK': str(int(track_number)),
    }
    print(json.dumps(metadata, indent=2))
    input('correct?')
    tag.write_wav_metadata(fpath=fpath, metadata=metadata)
