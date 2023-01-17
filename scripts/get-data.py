import json
from urllib.request import urlopen
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
import sys, traceback
from itertools import islice
import codecs

ipfs_hashes = {
        line.strip().split(",")[1]: line.strip().split(",")[0]
        for line in open("ipfs-hashes.csv").readlines() }

def check_url(url, entry):
    entry["mirror"] = []
#    if not skip_laundromat:
    uris = [f"ipfs:{ipfs_hashes[url]}"] if url in ipfs_hashes else []
    if uris:
        print(f"{url} => {uris[0]}")
        entry.update({
            "mirror": uris,
            "status": "OK"
        })
    else:
        try:
            r = requests.head(url,
                    allow_redirects=True, 
                    timeout=30)
            if r.status_code == 200:
                print(f"{url} OK")
                entry.update({
                    "status": "OK",
                    "media_type": str(r.headers["content-type"])
                    })
            else:
                print("%s %d" % (url, r.status_code))
                entry.update({
                    "status": "FAIL (%d)" % r.status_code
                    })
        except Exception as e:
            #traceback.print_exc(file=sys.stdout)
            print(f"{url} FAIL: ({str(e)})")
            entry.update({"status": f"FAIL ({str(e)})"})


def check_example(url, entry):
    try:
        r = requests.get(url,
                allow_redirects=True, 
                timeout=30,
                headers={"Accept":"application/rdf+xml,text/turtle,application/n-triples,application/ld+json,*/*q=0.9"})
        if r.status_code == 200:
            print(f"{url} OK")
            entry.update({
                "status": "OK",
                "media_type": str(r.headers["content-type"])
                })
        else:
            print("%s %d" % (url, r.status_code))
            entry.update({
                "status": "FAIL (%d)" % r.status_code
                })
    except Exception as e:
        #traceback.print_exc(file=sys.stdout)
        print(f"{url} FAIL: ({str(e)})")
        entry.update({"status": f"FAIL ({str(e)})"})



def check_sparql(url, entry):
    try:
        r = requests.head(url,
                allow_redirects=True, 
                timeout=30)
        if r.status_code == 200:
            print(f"{url} OK")
            entry.update({
                "status": "OK"
                })
        else:
            print("%s %d" % (url, r.status_code))
            entry.update({
                "status": "FAIL (%d)" % r.status_code
                })
    except Exception as e:
        #traceback.print_exc(file=sys.stdout)
        print(f"{url} FAIL: ({str(e)})")
        entry.update({"status": f"FAIL ({str(e)})"})


if __name__ == "__main__":
    #skip_laundromat = True
    reader = codecs.getreader("utf-8")
    data = json.load(reader(urlopen("https://lod-cloud.net/extract/datasets")))

    print("# Report for LOD Cloud availability")
    print()

    #data = list(islice(data.items(),2))
    data = data.items()

    for (identifier, dataset) in data:
        print("## Dataset name: " + dataset["identifier"])
        print()
        print("### Full Downloads (%d)" % len(dataset["full_download"]))
        print()

        for full_download in dataset["full_download"]:
           check_url(full_download["download_url"], full_download)
           print()

        print()
        print("### Other downloads (%d)" % len(dataset["other_download"]))

        if "other_download" in dataset:
            for other_download in dataset["other_download"]:
                if "access_url" in other_download:
                    check_url(other_download["access_url"], other_download)
                    print()

        if "example" in dataset:
            print("### Examples (%d)" % len(dataset["example"]))

            for example in dataset["example"]:
                if "access_url" in example:
                    check_example(example["access_url"], example)
                    print()

        if "sparql" in dataset:
            print("### SPARQL Endpoints (%d)" % len(dataset["sparql"]))

            for sparql in dataset["sparql"]:
                if "access_url" in sparql:
                    check_sparql(sparql["access_url"], sparql)
                    print()

        if "domain" in dataset and dataset["domain"] == "cross-domain":
            dataset["domain"] = "cross_domain"

        print()

    data = dict(data)

    with open("lod-data.json","w") as out:
        out.write(json.dumps(data, indent=2))

    resources = 0
    resources_available = 0
    links = {"full_download":0,"other_download":0,"example":0,"sparql":0}
    links_available = {"full_download":0,"other_download":0,"example":0,"sparql":0}

    for res in data.values():
        resources += 1
        success = False
        for (clazz,link_list) in res.items():
            if clazz in ["full_download","other_download","example","sparql"]:
                for link in link_list:
                    links[clazz] += 1
                    if link["status"] == "OK":
                        links_available[clazz] += 1
                        if not success:
                            success = True
                            resources_available += 1

    print("|                | Status    |")
    print("|----------------|-----------|")
    print("| Resources      | %4d/%4d |" % (resources_available, resources))
    print("| Full Download  | %4d/%4d |" % (links_available["full_download"], links["full_download"]))
    print("| Other Download | %4d/%4d |" % (links_available["other_download"], links["other_download"]))
    print("| Examples       | %4d/%4d |" % (links_available["example"], links["example"]))
    print("| SPARQL         | %4d/%4d |" % (links_available["sparql"], links["sparql"]))


