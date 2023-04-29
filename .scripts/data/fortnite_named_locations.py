import requests
from bs4 import BeautifulSoup

from core.utils import open_data_file

url = "https://fortnite.fandom.com/wiki/Named_Locations"
r = requests.get(url)

soup = BeautifulSoup(r.text, "html.parser")

with open_data_file("fortnite_named_locations") as f:
    f.write(f"# {url}\n")
    for body in soup.find("div", {"class": "tabber"}).find_all("tbody"):
        for i, tr in enumerate(body.find_all("tr")):
            if i == 0:
                continue
            f.write(tr.find("a").string + "\n")
