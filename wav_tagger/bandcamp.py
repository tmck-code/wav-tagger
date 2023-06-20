import json
import requests

def parse_tracks(data, album_artist):
    for track in data['track']['itemListElement']:
        yield {'track': track['position'], 'title': track['item']['name'], 'artist': album_artist}


response = requests.get('https://divididmusic.bandcamp.com/album/year-of-i')

for i, line in enumerate(response.text.split('\n')):
    if '/track/' in line.lower():
        try:
            data = json.loads(line.strip())
            for track in parse_tracks(data, 'Tom Finster'):
                print(track)
        except ValueError as e:
            print(':(', e, i)

