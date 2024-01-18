import requests

from core.utils import open_data_file, contains_swear

url = "https://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:English_proverbs&cmlimit=500&format=json"

cmcontinue = None
members = []
while True:
    if cmcontinue:
        r = requests.get(url + "&cmcontinue=" + cmcontinue)
    else:
        r = requests.get(url)
    data = r.json()
    for member in data["query"]["categorymembers"]:
        members.append(member["title"])
    if "continue" not in data:
        break
    cmcontinue = data["continue"]["cmcontinue"]

with open_data_file("proverbs") as f:
    f.write(f"# {url}\n")
    for member in members:
        if ":" in member or contains_swear(member):
            continue
        f.write(member + "\n")
