import json
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

if __name__ == '__main__':
    for t in fetch_tracks('https://polabryson.bandcamp.com/album/beneath-the-surface'):
        print(t)
