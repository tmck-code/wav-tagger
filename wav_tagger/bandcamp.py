import os
import re
import zipfile

def parse_track_metadata_from_fname(fname) -> tuple[str, dict]:
    m = re.match('(.*) - (.*) - (\d\d) (.*).wav', fname)
    if m is None:
        raise ValueError(f'could not parse {fname}')
    artist, album, track, title = m.groups()
    return album, artist, track, title

def parse_album_metadata_from_fname(fname) -> tuple[str, str]:
    m = re.match('(.*) - (.*).(zip|wav)', fname)
    artist, album, _ext = m.groups()
    return album, artist

def unzip(fpath) -> str:
    album, artist = parse_album_metadata_from_fname(os.path.basename(fpath))
    odirpath = f'{artist}/{album}'

    os.makedirs(odirpath, exist_ok=True)

    with zipfile.ZipFile(fpath, 'r') as zip_ref:
        zip_ref.extractall(odirpath)

    return odirpath
