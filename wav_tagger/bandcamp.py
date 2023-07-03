import json
import re
import zipfile

import requests

def parse_tracks(data):
    for track in data['track']['itemListElement']:
        yield {
            'track': track['position'],
            'title': track['item']['name'],
            'artist': data['albumArtist'],
        }

def fetch_metadata(url):
    response = requests.get(url)

    for i, line in enumerate(response.text.split('\n')):
        if '/track/' not in line.lower():
            continue
        try:
            return json.loads(line.strip())
        except ValueError as e:
            pass

def fetch_tracks(url):
    data = fetch_metadata(url)
    yield from parse_tracks(data)

def parse_track_metadata_from_fname(fname) -> (str, dict):
    m = re.match('(.*) - (.*) - (\d\d) (.*).wav', fname)
    if m is None:
        raise ValueError(f'could not parse {fname}')
    artist, album, track, title = m.groups()
    return album, {'artist': artist, 'track': track, 'title': title}

def parse_album_metadata_from_fname(fname) -> (str, str):
    m = re.match('(.*) - (.*).zip', fname)
    artist, album = m.groups()
    return album, artist

def unzip(fpath) -> str:
    album, artist = parse_album_metadata_from_fname(os.path.basename(fpath))
    odirpath = f'{artist}/{album}'

    os.makedirs(odirpath, exist_ok=True)

    with zipfile.ZipFile(fpath, 'r') as zip_ref:
        zip_ref.extractall(odirpath)

    return odirpath


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
    argparser.add_argument('-fpath', type=str, required=True)
    argparser.add_argument('-genre', type=str)
    args = argparser.parse_args().__dict__
    return args

if __name__ == '__main__':
    args = parse_args()

    # 1. unzip the file
    dirpath = unzip(args['fpath'])

    # 2. create metadata config by parsing filenames
    metadata = create_bandcamp_metadata(
        dirpath=dirpath,
        genre=args['genre'],
        ofpath='metadata.json'
    )
    ppd(asdict(metadata))

    # 3. apply the metadata
    choice = input('write metadata?')
    if choice.lower() in ('y', 'yes'):
        run_with_metadata(dirpath=args['dirpath'], metadata_fpath='metadata.json')



if __name__ == '__main__':
    for t in fetch_tracks(url=sys.argv[1]):
        print(t)
