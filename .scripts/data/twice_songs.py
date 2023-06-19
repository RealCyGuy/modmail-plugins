import requests

from core.utils import open_data_file

base_url = "https://api.spotify.com/v1"
token = input(
    "Enter Spotify access token (from https://developer.spotify.com/documentation/web-api/tutorials/getting-started#request-an-access-token): "
).strip()

headers = {"Authorization": f"Bearer {token}"}

album_ids = []
artist_id = "7n2Ycct7Beij7Dj7meI4X0"
url = f"{base_url}/artists/{artist_id}/albums?limit=50"
while True:
    r = requests.get(url, headers=headers)
    data = r.json()
    for album in data["items"]:
        album_ids.append(album["id"])
    url = data["next"]
    if not url:
        break

song_names = []
for i in range(0, len(album_ids), 20):
    ids = ",".join(album_ids[i : i + 20])
    url = f"{base_url}/albums?ids={ids}"
    r = requests.get(url, headers=headers)
    data = r.json()
    for album in data["albums"]:
        for track in album["tracks"]["items"]:
            art = False
            for artist in track["artists"]:
                if artist["id"] == artist_id:
                    art = True
            song_names.append(track["name"])

song_names = list(set(song_names))
song_names.sort()

with open_data_file("twice_songs") as f:
    f.write(f"# {base_url}\n")
    for song in song_names:
        f.write(song + "\n")
