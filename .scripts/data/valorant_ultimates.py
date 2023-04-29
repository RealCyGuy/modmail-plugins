import requests

from core.utils import open_data_file

url = "https://valorant-api.com/v1/agents?isPlayableCharacter=true"
r = requests.get(url)
data = r.json()

with open_data_file("valorant_ultimates") as f:
    f.write(f"# {url}\n")
    for agent in data["data"]:
        for ability in agent["abilities"]:
            if ability["slot"] == "Ultimate":
                f.write(ability["displayName"] + "\n")
