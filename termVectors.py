
from elasticsearch import Elasticsearch
es = Elasticsearch('http://localhost:9200')
from math import sqrt


keepwords = open('keepwords.txt').read()
keepwords = keepwords.split('\n')

def scoredFingerprint(terms):
    fp = {}
    for term, value in terms.items():
        if '_' in term:
            continue
        if value[1] < 100 or term in keepwords:
            fp[term] = (1.0)  #float(value['term_freq']) / float(value['doc_freq'])
        #else:
        #    print("Ommitting %s" % term)
    return fp

def scoredTvs(tvs, sampleEvery=1):
    i = 0
    for docId, tv in tvs:
        if (i % sampleEvery == 0):
            yield (docId, scoredFingerprint(tv))
        i += 1


def allCorpusDocs(index='stackexchange', doc_type='post'):
    query = {
        "sort": ["_doc"],
        "size": 500
    }
    resp = es.search(index=index, doc_type=doc_type, scroll='1m', body=query)
    i = 500
    while len(resp['hits']['hits']) > 0:
        for doc in resp['hits']['hits']:
            yield doc['_id']
        print("Retrieved %s ids" % i)
        i += 500
        scrollId = resp['_scroll_id']
        resp = es.scroll(scroll_id=scrollId, scroll='1m')


def justTfandDf(terms):
    tfAndDf = {}
    for term, value in terms.items():

        tfAndDf[term] = (value['term_freq'], value['doc_freq'])
    return tfAndDf

def termVectors(docIds, index='stackexchange', doc_type='post', field='Body.bigramed'):
    tvs = es.mtermvectors(ids=docIds, index=index, doc_type=doc_type, fields=field, term_statistics=True)
    for tv in tvs['docs']:
        try:
            yield (tv['_id'], justTfandDf(tv['term_vectors'][field]['terms']))
        except KeyError:
            pass


def groupEveryN(l, n=10):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def allTermVectors(docIds, field='Body.bigramed'):
    i = n = 100
    for docIdGroup in groupEveryN(docIds, n=n):
        for tv in termVectors(docIds=docIdGroup, field=field):
            yield tv
        print("Fetched %s termvectors" % i)
        i += n

def say(a_list):
    print(" ".join(a_list))

tdc = None

def buildStackexchange(field='Body.bigramed', numTopics=50, sampleEvery=1):
    import pickleCache
    docIds = tvs = None
    try:
        docIds = pickleCache.fetch('docIds')
    except KeyError:
        print("Fetching docIds from ES")
        docIds = [docId for docId in allCorpusDocs()]
        pickleCache.save('docIds', docIds)

    print("Fetching %s Term Vectors" % len(docIds))

    from lsi import TermDocCollection

    try:
        tvs = pickleCache.fetch(field + '.tws')
    except KeyError:
        tvs = [tv for tv in allTermVectors(docIds, field=field)]
        pickleCache.save(field + '.tws', tvs)

    tdc = TermDocCollection(scoredTvs(tvs, sampleEvery=sampleEvery), numTopics=numTopics)
    print(tdc.getTermvector('11336'))
    blurred = tdc.getBlurredTerms('11336')
    print(blurred[1][:10])

    return tdc


if __name__ == "__main__":
    from sys import argv
    buildStackexchange(argv[1], 150)
    print("DEMO AUTOGEN SYNONYMS FOR DOCUMENTS")
    print("\n**star wars document**")
