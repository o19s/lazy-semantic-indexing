

from lsi import Index

def asTermVect(doc, useDf=True, addTf=True):
    """ A simple string to a term vector"""
    tv = {}
    terms = doc.lower().split()
    for term in terms:
        df = 1.0
        if useDf and term in ['a', 'the']:
            df = 13.0
        elif useDf and term in ['dog', 'puppy']:
            df = 5.0
        elif useDf and term in ['cat']:
            df = 3.0
        elif useDf and term in ['fish', 'water', 'pooch', 'meow']:
            df = 2.0
        try:
            if addTf:
                tv[term] += (1.0 / df)
            else:
                tv[term] = (1.0 / df)
        except KeyError:
            tv[term] = (1.0 / df)
    return tv



# Some dumb docs over a limited vocabulary
#

semIdx = Index(source=[("0", asTermVect("a dog a puppy")),
                       ("1", asTermVect("a cat a kitty")),
                       ("2", asTermVect("a dog puppy")),
                       ("3", asTermVect("a cat a meow")),
                       ("4", asTermVect("a dog a pooch")),
                       ("5", asTermVect("a dog a puppy")),
                       ("6", asTermVect("a dog a puppy")),
                       ("7", asTermVect("a cat a meow")),
                       ("8", asTermVect("a fish a water")),
                       ("9", asTermVect("a water a fish")),
                       ("10", asTermVect("a water a fish fish")),
                       ("11", asTermVect("a water a water fish")),
                       ("12", asTermVect("a puppy a pooch"))], numTopics=5)


colMatrx = semIdx._getCscMatrix()
print("M %s" % colMatrx)


u,s,v = semIdx._getSvd();

print("U  %s" % u)
print("S  %s" % s)
print("V  %s" % v)

print("Up %s" % semIdx._getUprime())

print("---TOPICS---")
print("top 0 %s" % semIdx.getTopic(0, cutoff=-5)[:5])
print("top 1 %s" % semIdx.getTopic(1, cutoff=-5)[:5])
print("top 2 %s" % semIdx.getTopic(2, cutoff=-5)[:5])
print("top 3 %s" % semIdx.getTopic(3, cutoff=-5)[:5])
print("top 4 %s" % semIdx.getTopic(4, cutoff=-5)[:5])

#print("---DOCS---")
#print("doc 0 %s" % semIdx.getBlurredTerms('0', cutoff=-5)[1])
#print("doc 1 %s" % semIdx.getBlurredTerms('1', cutoff=-5)[1])
#print("doc 2 %s" % semIdx.getBlurredTerms('2', cutoff=-5)[1])
