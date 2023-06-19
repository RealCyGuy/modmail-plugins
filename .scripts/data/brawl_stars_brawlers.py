import requests

from core.utils import open_data_file

url = "https://api.brawlapi.com/v1/brawlers"
r = requests.get(url)
data = r.json()

with open_data_file("brawl_stars_brawlers") as f:
    f.write(f"# {url}\n")
    for brawler in data["list"]:
        f.write(brawler["name"] + "\n")
