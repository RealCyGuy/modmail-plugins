import requests

from core.utils import open_data_file

url = "https://api.brawlapi.com/v1/maps"
r = requests.get(url)
data = r.json()

with open_data_file("brawl_stars_duos_maps") as f:
    f.write(f"# {url}\n")
    for brawl_map in data["list"]:
        if brawl_map["gameMode"]["hash"] == "Duo-Showdown":
            f.write(brawl_map["name"] + "\n")
