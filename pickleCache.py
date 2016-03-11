import os
import pickle

def fetch(key):
    key = key + '.pickle'
    if os.path.isfile(key):
        return pickle.load(open(key, 'rb'))
    raise KeyError("%s not in pickle cache" % key)

def save(key, data):
    key = key + '.pickle'
    pickled = pickle.dumps(data)
    f = open(key, 'wb')
    f.write(pickled)
    f.close()
