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


stopwords = open('long_stopwords.txt').read().split('\n')

def randomWords(words, n=50):
    # dedup the words
    import random
    import string
    uniqWords = set([word.lower().strip(string.punctuation) for word in words])
    stoppedWords = [word for word in uniqWords if word not in stopwords]
    if len(stoppedWords) > n:
        return random.sample(stoppedWords, n)
    else:
        return stoppedWords


import json
def mungePosts():
    posts = json.loads(open('scifi_stackexchange.json').read())

    for post in posts:
        try:
            body = randomWords(strip_tags(post['Body']).split())
            yield (post['Id'],  body)
        except ValueError:
            pass

if __name__ == "__main__":
    with open('scifi_stackexchange_rand.json', 'w') as f:

        munged = []
        for post in mungePosts():
            munged.append({'Id': post[0], 'Body': " ".join(post[1])})
        f.write(json.dumps(munged))
