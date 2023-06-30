import json
import re

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

def parse_metadata_from_fname(fname) -> (str, dict):
    m = re.match('(.*) - (.*) - (\d\d) (.*).wav', fname)
    if m is None:
        raise ValueError(f'could not parse {fname}')
    artist, album, track, title = m.groups()
    return album, {'artist': artist, 'track': track, 'title': title}


if __name__ == '__main__':
    for t in fetch_tracks(url=sys.argv[1]):
        print(t)
