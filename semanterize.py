from search_index import termVectors, docIds
from math import sqrt, log

def scoredFingerprint(terms, docCount, totalTermCount, uniqueTermCount):
    keepwords = open('keepwords.txt').read()
    keepwords = keepwords.split('\n')

    fp = {}
    average = uniqueTermCount / docCount
    distanceFromAverage = abs(average - len(terms))

    thisLen = 0
    for term, value in terms.items():
        thisLen += value[0]

    for term, value in terms.items():
        fp[term] = 1.0
        #if '_' in term:
        #    continue
        #if value[1] < 800 or term in keepwords:
        #    fp[term] = 1.0 / value[1] #(0.1 * distanceFromAverage + 1.0) #sqrt(value[0]) / (log(len(terms)))
        #else:
        #    continue
            #print("Ommitting %s" % term)

        #print("Dist from avg(%s) %s" % (average, distanceFromAverage))
        #try:
        #    fp[term] += (1.0) # / value[1]  #float(value['term_freq']) / float(value['doc_freq'])
        #except KeyError:
        #    fp[term] = (1.0) # / value[1]  #float(value['term_freq']) / float(value['doc_freq'])

    return fp

def scoredTvs(tvs, sampleEvery=1):
    i = 0
    # compute an average length (in number of terms)
    totalTermCount = 0.0
    uniqueTermCount = 0.0
    docCount = len(tvs)
    for docId, tv in tvs:
        for term, value in tv.items():
            totalTermCount += value[0]
            uniqueTermCount += 1.0


    for docId, tv in tvs:
        if (i % sampleEvery == 0):
            yield (docId, scoredFingerprint(tv, docCount, totalTermCount, uniqueTermCount))
        i += 1


def buildStackexchange(field='Body.bigramed', numTopics=100, sampleEvery=1, index='stackexchange_grams'):
    from elasticsearch import Elasticsearch
    es = Elasticsearch('http://localhost:9200')
    import pickleCache
    seDocIds = tvs = None
    try:
        seDocIds = pickleCache.fetch('docIds')
    except KeyError:
        print("Fetching docIds from ES")
        seDocIds = [docId for docId in docIds(es, index=index)]
        pickleCache.save('docIds', seDocIds)

    print("Fetching %s Term Vectors" % len(seDocIds))

    from lsi import Index

    try:
        tvs = pickleCache.fetch(field + '.tws')
    except KeyError:
        tvs = [tv for tv in termVectors(es, seDocIds, field=field, index=index)]
        pickleCache.save(field + '.tws', tvs)

    tdc = Index(scoredTvs(tvs, sampleEvery=sampleEvery), numTopics=numTopics)
    print("---BLURRED DOCS---")
    print(tdc.getTermvector('11336'))
    blurred = tdc.getBlurredTerms('11336')
    print(blurred[1][:10])
    print(tdc.getTermvector('100829'))
    blurred = tdc.getBlurredTerms('100829')
    print(blurred[1][:10])

    print("---TOPICS(terms)---")
    print("top 0 %s" % tdc.getTopic(0, cutoff=-50)[:15])
    print("top 1 %s" % tdc.getTopic(1, cutoff=-50)[:15])
    print("top 2 %s" % tdc.getTopic(2, cutoff=-50)[:15])
    print("top 3 %s" % tdc.getTopic(3, cutoff=-50)[:15])
    print("top 4 %s" % tdc.getTopic(4, cutoff=-50)[:15])

    print("\n---TOPICS(docs)---")
    print("top 0 %s" % tdc.getTopicDocs(0, cutoff=-50)[:15])
    print("top 1 %s" % tdc.getTopicDocs(1, cutoff=-50)[:15])
    print("top 2 %s" % tdc.getTopicDocs(2, cutoff=-50)[:15])
    print("top 3 %s" % tdc.getTopicDocs(3, cutoff=-50)[:15])
    print("top 4 %s" % tdc.getTopicDocs(4, cutoff=-50)[:15])

    return tdc

if __name__ == "__main__":
    from sys import argv
    buildStackexchange(field=argv[1])
