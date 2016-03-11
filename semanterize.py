from search_index import termVectors, docIds

def scoredFingerprint(terms):
    keepwords = open('keepwords.txt').read()
    keepwords = keepwords.split('\n')

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


def buildStackexchange(field='Body.bigramed', numTopics=50, sampleEvery=1):
    from elasticsearch import Elasticsearch
    es = Elasticsearch('http://localhost:9200')
    import pickleCache
    seDocIds = tvs = None
    try:
        seDocIds = pickleCache.fetch('docIds')
    except KeyError:
        print("Fetching docIds from ES")
        seDocIds = [docId for docId in docIds(es)]
        pickleCache.save('docIds', docIds)

    print("Fetching %s Term Vectors" % len(seDocIds))

    from lsi import Index

    try:
        tvs = pickleCache.fetch(field + '.tws')
    except KeyError:
        tvs = [tv for tv in termVectors(es, seDocIds, field=field)]
        pickleCache.save(field + '.tws', tvs)

    tdc = Index(scoredTvs(tvs, sampleEvery=sampleEvery), numTopics=numTopics)
    print(tdc.getTermvector('11336'))
    blurred = tdc.getBlurredTerms('11336')
    print(blurred[1][:10])

    return tdc

if __name__ == "__main__":
    from sys import argv
    buildStackexchange(field=argv[1])
