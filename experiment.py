

from lsi import Index

def asTermVect(doc):
    """ A simple string to a term vector"""
    tv = {}
    terms = doc.lower().split()
    for term in terms:
        try:
            tv[term] += 1
        except KeyError:
            tv[term] = 1
    return tv



# Some dumb docs over a limited vocabulary
#

semIdx = Index(source=[("0", asTermVect("The bear eats")),
                       ("1", asTermVect("The dog")),
                       ("2", asTermVect("The cat eats the dog"))], numTopics=3)

# Input matrix

#    0 1 2
#
#0   1   1  eats
#1   1 1 2  the
#2   1      bear
#3     1 1  dog
#4       1  cat
#
#
# U (term -> genre)
#
# [[-0.13304947 -0.77986221 -0.39744915 -0.38241306 -0.26439968]
#  [ 0.67116681 -0.04095141  0.48581725 -0.52676867 -0.18534956]
#  [-0.3960214  -0.12303622  0.32560062 -0.44863685  0.72162203]]
#
#
#


colMatrx = semIdx._getCscMatrix()
print("M %s" % colMatrx)


u,s,v = semIdx._getSvd();

print("U  %s" % u)
print("S  %s" % s)
print("V  %s" % v)

print("Up %s" % semIdx._getUprime())

print("top 0 %s" % semIdx.getTopic(0, cutoff=-5))
print("top 1 %s" % semIdx.getTopic(1, cutoff=-5))
print("top 2 %s" % semIdx.getTopic(2, cutoff=-5))

print("doc 0 %s" % semIdx.getBlurredTerms('0', cutoff=-5)[1])
print("doc 1 %s" % semIdx.getBlurredTerms('1', cutoff=-5)[1])
print("doc 2 %s" % semIdx.getBlurredTerms('2', cutoff=-5)[1])
