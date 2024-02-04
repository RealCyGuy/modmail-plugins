import requests

from core.utils import open_data_file

url = "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database-minified.json"
r = requests.get(url)
data = r.json()

with open_data_file("anime") as f:
    f.write(f"# {url}\n")
    for anime in data["data"]:
        if anime["type"] == "TV" and anime["episodes"] > 1:
            for source in anime["sources"]:
                if "anilist" in source:
                    f.write(f"{source[source.rindex('/') + 1:]} {anime['title']}\n")
                    break
