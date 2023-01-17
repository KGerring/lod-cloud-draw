import re
import json

data = json.load(open("lod-data.json"))


def toint(y):
    if isinstance(y, int):
        return y
    x = y.replace(",","").replace(".","")
    return int(x) if re.match("^[0-9]+$", x) else 0

print("Triples")
print(sum(toint(x["triples"]) for x in data.values()))
print("")
print("Links")
print(sum(toint(x["value"])  for y in data.values() for x in y["links"]))
