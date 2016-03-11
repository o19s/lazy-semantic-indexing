def docIds(es, index='stackexchange', doc_type='post'):
    """ Fetch the id of all docs of type "doc_type" from "index"""""
    query = {
        "sort": ["_doc"], # docs indicate this as the most efficient way to just iterate
                          # over the corpus if you don't care about performance
        "size": 500
    }
    resp = es.search(index=index, doc_type=doc_type, scroll='1m', body=query)
    batchSize = 500
    i = batchSize
    while len(resp['hits']['hits']) > 0:
        for doc in resp['hits']['hits']:
            yield doc['_id']
        print("Retrieved %s ids" % i)
        i += batchSize
        scrollId = resp['_scroll_id']
        resp = es.scroll(scroll_id=scrollId, scroll='1m')


def justTfandDf(terms):
    """ Format the stats for each term into a compact tuple"""
    tfAndDf = {}
    for term, value in terms.items():

        tfAndDf[term] = (value['term_freq'], value['doc_freq'])
    return tfAndDf

def _termVectorBatch(es, docIds, index='stackexchange', doc_type='post', field='Body.bigramed'):
    """ Returns term vectors for specified batch of docIds
        for each docid yields the format:
        (docId1, {term1: (tf, df), term2: (tf, df)...}, docId2)"""
    tvs = es.mtermvectors(ids=docIds, index=index, doc_type=doc_type, fields=field, term_statistics=True)
    for tv in tvs['docs']:
        try:
            yield (tv['_id'], justTfandDf(tv['term_vectors'][field]['terms']))
        except KeyError:
            pass


def groupEveryN(l, n=10):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def termVectors(es, docIds, field='Body.bigramed'):
    """ Returns term vectors for corpus one doc at a time
        for each docid yields the format:
        (docId1, {term1: (tf, df), term2: (tf, df)...})"""
    i = n = 100
    for docIdGroup in groupEveryN(docIds, n=n):
        for tv in _termVectorBatch(es, docIds=docIdGroup, field=field):
            yield tv
        print("Fetched %s termvectors" % i)
        i += n
