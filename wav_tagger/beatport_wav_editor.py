#!/usr/bin/env python3

import os, sys, json, glob
from itertools import count

import ffmpeg
import requests

FF_META = "out.txt"

def parse_metadata(fpath):
    (
        ffmpeg
            .input(fpath)
            .output(FF_META, format="ffmetadata", loglevel="quiet")
            .overwrite_output()
            .run()
    )
    data = open(FF_META, 'rb').read().decode(errors='replace').strip().split("\n")
    # os.remove(FF_META)
    print(data)
    return dict([
        tuple(l.split("=", 1)) for l in data[3:]
    ])

def write_metadata(fpath: str, metadata: dict, ofpath: str):
    with open(FF_META, "w") as ostream:
        ostream.write(";FFMETADATA1\n")
        ostream.write("\n".join("=".join([k,v]) for k,v in metadata.items()))
    (
        ffmpeg
            .input(fpath)
            .output(ofpath, codec="copy", map_metadata="1", loglevel="quiet")
            .global_args("-i", FF_META)
            .overwrite_output()
            .run()
    )
    os.remove(FF_META)

def _gen_metadata_args(metadata: dict) -> dict:
    return {f"metadata:g:{i}": f"{k}={v}" for i,(k,v) in zip(count(), metadata.items())}

def format_artist_names(artists: list):
    return " & ".join([", ".join(artists[0:-1]), artists[-1]]).lstrip(" & ")

def grab_release_url(fpath):
    s = fpath.split("-")[0::2]
    url = "http://beatport.com/track/"+s[1].replace("_", "-").lower()+"/"+s[0]
    r = requests.get(url)
    for l in r.iter_lines():
        if b'"@type": "BreadcrumbList"' in l:
            for k in json.loads(l.strip().decode())[0]["itemListElement"]:
                if "release" in k["item"]["@id"]:
                    return k["item"]["@id"]

def grab_track_info(fpath):
    track_id = int(fpath.split("-")[0])
    url = grab_release_url(fpath)
    r = requests.get(url)

    for l in r.iter_lines():
        if b"catalogNumber" in l:
            release_info = json.loads(l.strip())[1]

        if b"window.Playables" in l:
            data = json.loads(l.strip().decode().split(" = ")[1][:-1])
            for i, track in enumerate(data["tracks"]):
                if track["id"] == track_id:
                    track_info = track
                    track_info["track_number"] = str(i+1)

    title = track_info["name"]
    if "remix" in track_info["mix"].lower():
         title = title + f" ({track_info['mix']})"

    return {
        "title": title,
        "artist": format_artist_names([t["name"] for t in track_info["artists"]]),
        "album": release_info["name"] + f' [{release_info["catalogNumber"]}]',
        "genre": track_info["genres"][0]["name"],
        "track": track_info["track_number"],
    }



if __name__ == '__main__':
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

