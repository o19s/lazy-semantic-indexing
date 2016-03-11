import requests
import json


def openPosts():
    data = ""
    try:
        f = open("scifi_stackexchange.json")
        data = f.read()
    except IOError:
        stackExchangeData ="https://storage.googleapis.com/quepid-sample-datasets/elasticsearch/scifi_stackexchange.json"
        resp = requests.get(stackExchangeData)
        print("GET %s Len %s" % (resp.status_code, len(resp.text)))
        f = open("scifi_stackexchange.json", "w")
        f.write(resp.text)
        data = resp.text
        f.close()
    return json.loads(data)

print("Opening Posts")
posts = openPosts()
print("Got %s posts" % len(posts))

def bulkAdds(posts, index='stackexchange'):
    print("Indexing %s Posts" % len(posts))
    for post in posts:
        print("indexing %s" % post['Id'])
        yield {
                "_id": post['Id'],
                "_index": index,
                '_type': 'post',
                '_op_type': 'index',
                '_source': post
              }


from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
es = Elasticsearch("http://localhost:9200")

bulk(es, bulkAdds(posts))
