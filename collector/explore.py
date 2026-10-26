import json
from collections import Counter

with open("raw_sample.json", encoding="utf-8") as f:
    data = json.load(f)

for k, v in data[0].items():
    print(f"{k:45} {type(v).__name__:8} {v}")

nulls = Counter(k for row in data for k, v in row.items() if v is None)
print("\nNans:", dict(nulls))