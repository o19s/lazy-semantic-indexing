import scipy.sparse
import numpy
import sparsesvd

from collections import defaultdict


class StringIndexDict(object):
    """
    A 2-way dict-like object that only has functionality for getting and item.
    If you get with a string key, it will return the integer associated with that key.
    If you get with a integer key, it will return the string associated with that key.
    If you get an item that's currently not there, then the dict will return the next available
    integer (unique) and return that. If you call freeze on the dict, then nothing more
    can be added to it.
    """
    def __init__(self):
        self.currentIndex = -1
        self.stringDict = defaultdict(self._increment)
        self.indexDict = {}

    def _increment(self):
        self.currentIndex += 1
        self.indexDict[self.currentIndex] = self.keyInQuestion #kinda funky, but since this will always be single threaded, it's ok
        return self.currentIndex

    def __getitem__(self,key):
        self.keyInQuestion = key
        if isinstance(key,str):
            return self.stringDict[key]
        else :
            return self.indexDict[key]

    def size(self):
        return self.currentIndex + 1

    def freeze(self):
        #allow no more changes
        self.stringDict.default_factory = None



class Index(object):
    """ SemanticIndex represents the results of the SVD operation over
        a term-document matrix
    """
    def __init__(self,source=None,numTopics=10):
        # Source is a list of tuples, first element being docId,
        # second element the term vector (why isn't this a dict?)
        self._docDict = StringIndexDict()
        self._termDict = StringIndexDict()
        self._termVectors = []
        self.numTopics = numTopics
        for termVector in source:
            self._termVectors.append( #append tuple of (docNum, {termNum_i,numberOccurrences_i})
                (
                    self._docDict[termVector[0]],
                    {self._termDict[k]:v for k,v in termVector[1].items()}
                )
            )
        self._termDict.freeze()
        self._docDict.freeze()
        self.numTerms = self._termDict.size()
        self.numDocs = self._docDict.size()

        #memoized later:
        self._svd = None
        self._cscMatrix = None
        self._uPrime = None
        self._uStripped = None


    def _getCscMatrix(self):#compressed sparse column matrix
        if self._cscMatrix is not None:
            return self._cscMatrix
        # data and indices are parallel arrays,
        # data storing values (ie tf*idf) and indices storing values
        num_nnz, data, indices, indptr = 0, [], [], [0]
        for termVector in self._termVectors:
            newIndices = [i for i in termVector[1].keys()]
            newValues = [v for v in termVector[1].values()]
            indices.extend(newIndices)
            data.extend(newValues)
            num_nnz += len(newValues)
            indptr.append(num_nnz)
        data = numpy.asarray(data)
        indices = numpy.asarray(indices)
        # compressed sparse column matrix
        # Rows terms, column docs
        #
        #        doc1   doc2   doc3
        # 'the'    1      1     1
        # 'cat'    1      0     2
        self._cscMatrix = scipy.sparse.csc_matrix((data, indices, indptr),
                shape=(self.numTerms, self.numDocs))
        return self._cscMatrix

    def _getSvd(self):
        if self._svd is not None:
            return self._svd
        self._svd = sparsesvd.sparsesvd(self._getCscMatrix(), self.numTopics)
        return self._svd

    def _getUprime(self, stops=0, drops=0):
        """ u combined with the strength of each topic (s)"""
        #if self._uPrime is not None:
        #    return self._uPrime
        # u is
        u,s,v = self._getSvd()
        for stop in range(stops): #rank reduce by most common (ie stop words)
            s[stop] = 0
        for drop in range(drops):
            s[-drop] = 0
        self._uPrime = numpy.dot(u.T,numpy.diag(s))
        return self._uPrime

    def getTermvector(self,docId):
        """ Get the initial term vector for docid doc"""
        print("TV for %s" % docId)
        if isinstance(docId,str):
            doc = self._docDict[docId]
        tv = self._termVectors[doc]
        return {self._termDict[k]: v for k, v in tv[1].items()}

    def getBlurredTerms(self,docId,cutoff=0,stops=0,drops=0):
        print("Fetching for %s" % docId)
        if isinstance(docId,str):
            doc = self._docDict[docId]
        # term-genre affinities
        uPrime = self._getUprime(stops=stops,drops=drops)
        # v is the doc-genre affinities
        _,_,v = self._getSvd()
        # doc product for a specific document and term-genre affinities
        blurredField = numpy.dot(uPrime,v[:,doc])
        tokenStrengths = numpy.where(blurredField > cutoff, blurredField, 0)
        tokens = [(self._termDict[termId], strength) for (termId, strength) in enumerate(tokenStrengths)]
        tokens.sort(key=lambda x: abs(x[1]), reverse=True)

        return (self._docDict[doc], tokens)

    def _getStrippedUprime(self):
        #returns uPrime except that each word is only associated with their maximum
        #score in any topic (all other values are set to 0). This might give better
        #results for topic word lists
        if self._uStripped is not None:
            return self._uStripped
        uPrime = self._getUprime()
        uStripped = numpy.zeros(uPrime.shape)
        for termIndex in range(uPrime.shape[0]):
            maxIndex = numpy.argmax(uPrime[termIndex])
            uStripped[termIndex,maxIndex] = uPrime[termIndex,maxIndex]
        self._uStripped = uStripped
        return uStripped

    def getTopic(self,topicNum,cutoff=0,stripped=False):
        if stripped:
            uPrime = self._getStrippedUprime()
        else:
            uPrime = self._getUprime()

        uPrimeTopic = uPrime.T[topicNum]

        topicTermByStr = [(self._termDict[i], uPrimeTopic[i])
                           for i in numpy.where(uPrimeTopic>cutoff)[0]
                          ]
        topicTermByStr.sort(key=lambda x: abs(x[1]), reverse=True)
        return topicTermByStr

    def getRelatedTerms(self,token,numTerms,tokens_only=True):
        uP = self._getUprime()
        termDict = self._termDict
        u,_,_ = self._getSvd()
        strength_and_indices = sorted( zip(numpy.dot(uP[termDict[token]],u),range(len(uP))) , reverse=True )
        method = 0
        if tokens_only:
            method = lambda i: termDict[i[1]]
        else:
            method = lambda i: (termDict[i[1]],i[0])
        return  [ method(i) for i in strength_and_indices[:numTerms] ]

