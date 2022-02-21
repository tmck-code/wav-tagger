import beatport_wav_editor

def test_gen_args():
    result = beatport_wav_editor._gen_metadata_args({
        'title': 'My Title',
        'artist': 'Me',
        'album': 'X',
        'year': '2019'
    })
    expected = {
        'metadata:g:0': 'title=My Title',
        'metadata:g:1': 'artist=Me',
        'metadata:g:2': 'album=X',
        'metadata:g:3': 'year=2019'
    }
    assert expected == result

def test_format_artist_names():
    tests = (
        (["me"], "me"),
        (["me", "myself"], "me & myself"),
        (["me", "myself", "i"], "me, myself & i"),
        (["me", "myself", "i", "another"], "me, myself, i & another"),
    )
    for val, expected in tests:
        assert expected == beatport_wav_editor.format_artist_names(val)
