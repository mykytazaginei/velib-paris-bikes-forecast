import json
import requests
from collections import Counter

URL = ("https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
       "velib-disponibilite-en-temps-reel/exports/json")

resp = requests.get(URL, timeout=30)
resp.raise_for_status()
data = resp.json()

with open("raw_sample.json", encoding="utf-8") as f:
    data = json.load(f)

for k, v in data[0].items():
    print(f"{k:45} {type(v).__name__:8} {v}")

nulls = Counter(k for row in data for k, v in row.items() if v is None)
print("\nNans:", dict(nulls))