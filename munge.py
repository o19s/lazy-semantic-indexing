


class MungedPost:

    def __init__(self):
        self.munged = {}

    def addBody(self, bodyText):
        try:
            self.munged['body'].append(bodyText)
        except KeyError:
            self.munged['body'] = [bodyText]


    def addTitle(self, titleText):
        if 'titleText' not in self.munged:
            self.munged['titleText'] = titleText
            self.addBody(titleText)


import json
def mungePosts():
    posts = json.loads(open('scifi_stackexchange.json').read())

    POSTTYPE_QUESTION = '1'
    POSTTYPE_ANSWER = '2'

    allMunged = {}
    for post in posts:
        body = post['Body']
        questionId = post['Id']
        title = None
        if post['PostTypeId'] == POSTTYPE_ANSWER:
            questionId = post['ParentId']
        elif post['PostTypeId'] == POSTTYPE_QUESTION:
            title = post['Title']
        else: # wiki text and what-not
            continue

        try:
            allMunged[questionId].addBody(body)
        except KeyError:
            allMunged[questionId] = MungedPost()
            allMunged[questionId].addBody(body)

        if title:
            allMunged[questionId].addTitle(title)
    return allMunged

if __name__ == "__main__":
    f = open('scifi_stackexchange_munged.json', 'w')

    munged = []
    for qId, post in mungePosts().items():
        try:
            munged.append({'Id': qId, 'Body': post.munged['body'], 'Title': post.munged['titleText']})
        except KeyError:
            print("Omitting %s" % qId)
    f.write(json.dumps(munged))
    f.close()
