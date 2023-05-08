from wav_tagger import tag

def test_write_wav_metadata():
    wav_fpath = 'test/data/sin-200Hz.wav'
    data = {
        'title': 'yolo',
        'artist': 'me',
        'album': 'my album',
    }
    tag.write_wav_metadata(wav_fpath, data)

