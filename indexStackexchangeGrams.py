import json


def openPosts():
    data = ""
    f = open("scifi_stackexchange_grams.json")
    data = f.read()
    return json.loads(data)

print("Opening Posts")
posts = openPosts()
print("Got %s posts" % len(posts))

def bulkAdds(posts, index='stackexchange_grams'):
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
