from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from core.utils import open_data_file

url = "https://bulbapedia.bulbagarden.net/wiki/List_of_moves"
r = requests.get(url)

soup = BeautifulSoup(r.text, "html.parser")

with open_data_file("pokemon_moves") as f:
    f.write(f"# {url}\n")
    table = soup.find("div", {"id": "mw-content-text"}).find("table").find("table")
    for a in soup.select("div#mw-content-text table:first-of-type table tbody > tr > td:nth-child(2) > a"):
        f.write(f"[{a.string}](<{urljoin(url, a['href'])}>)\n")
