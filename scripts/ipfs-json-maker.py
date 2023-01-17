import json
from urllib.request import urlopen
import codecs
import os


reader = codecs.getreader("utf-8")
data = json.load(reader(urlopen("https://lod-cloud.net/extract/datasets")))

print("# IPFS JSON")

#data = list(islice(data.items(),2))
data = data.items()

newDict = {}


print(len(data))
counter=0
for (identifier, dataset) in data:
    if "other_download" in dataset:
        #print(identifier)
        for other_download in dataset["other_download"]:
        	 

            if (
                'mirror' in other_download.keys()
                and len(other_download['mirror']) > 0
            ):
                newDict[identifier] = dataset
                counter=counter+1

print(counter)



with open(f"{os.path.dirname(os.path.abspath(__file__))}../ipfs-lod.json", "w") as out:
    out.write(json.dumps(newDict, indent=2))
