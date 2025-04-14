#!/usr/bin/env python3

import argparse
import glob
import json

from wav_tagger import tag

def read_metadata(fpaths: str, ofpath: str):
    print('reading metadata from', fpaths)
    writer = tag.MetadataWriter()
    with open(ofpath, 'w') as ostream:
        for fpath in fpaths:
            print('reading metadata from', fpath)
            metadata = writer.read_from_wav(fpath)._asdict() | {'fpath': fpath}
            print(json.dumps(metadata, indent=2))
            print(json.dumps(metadata), file=ostream)


def write_metadata(fpath: str, metadata: dict):
    print('writing metadata to', fpath)
    tag.MetadataWriter().write_to_wav(
        metadata  = tag.WavMetadata(**metadata),
        wav_fpath = fpath
    )

def main(mode: str, kwargs: dict):
    match mode:
        case 'read':
            if kwargs.get('dirpath') is not None:
                read_metadata(glob.glob(f'{kwargs["dirpath"]}/*wav'), kwargs['ofpath'])
            else:
                read_metadata([kwargs['fpath']], kwargs['ofpath'])
        case 'write':
            for m in map(json.loads, open(kwargs['metadata'], 'r')):
                fpath = m.pop('fpath')
                write_metadata(fpath, m)
        case _:
            raise ValueError(f'Unknown mode: {mode}')

def parse_args():
    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(dest='mode')

    # takes a wav file and writes its metadata to a json file
    read_parser = subparsers.add_parser('read')
    read_parser.add_argument('-fpath', type=str)
    read_parser.add_argument('-dirpath', type=str)
    read_parser.add_argument('-ofpath', type=str, required=True)

    # takes a metadata file in json format and writes it to a wav file
    write_parser = subparsers.add_parser('write')
    write_parser.add_argument('-metadata', type=str, required=True)

    d = argparser.parse_args().__dict__
    mode = d.pop('mode')

    return mode, d

if __name__ == '__main__':
    main(*parse_args())
