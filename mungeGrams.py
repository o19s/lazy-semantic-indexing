from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def skipGrams(words, n=8):
    for startIdx, startWord in enumerate(words):
        for nxt in range(startIdx + 1, startIdx+n):
            if nxt < len(words):
                yield (startWord, words[nxt])


import json
def mungePosts():
    posts = json.loads(open('scifi_stackexchange.json').read())

    for post in posts[:2000]:
        body = post['Body']
        for idx, gram in enumerate(skipGrams(strip_tags(body).split())):
            gramId = "%s_%s" % (post['Id'], idx)
            yield (gramId,  gram)

if __name__ == "__main__":
    with open('scifi_stackexchange_grams.json', 'w') as f:

        munged = []
        f.write('[') # evil manual json formatting to save RAM
        for idx, post in enumerate(mungePosts()):
            if idx > 0:
                f.write(',\n')
            f.write(json.dumps({"Id": post[0], "Body": " ".join(post[1])}))
        f.write(']')
