import requests

from core.utils import open_data_file

url = (
    "https://en.wiktionary.org/w/api.php?action=query&cmlimit=500&cmprop=title&cmtitle=Category"
    "%3AEnglish_terms_suffixed_with_-phobia&list=categorymembers&format=json"
)

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

with open_data_file("phobias") as f:
    f.write(f"# {url}\n")
    for member in members:
        f.write(member + "\n")
