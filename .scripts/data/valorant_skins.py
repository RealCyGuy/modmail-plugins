import requests

from core.utils import open_data_file

url = "https://valorant-api.com/v1/weapons/skins"
r = requests.get(url)
data = r.json()

with open_data_file("valorant_skins") as f:
    f.write(f"# {url}\n")
    for weapon in data["data"]:
        display_name = weapon["displayName"]
        f.write(display_name + "\n")
