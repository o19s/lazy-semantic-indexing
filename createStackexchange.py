analyzers = {
    "filter" : {
        "bigram_filter": {
                "type": "shingle",
                "max_shingle_size":2,
                "min_shingle_size":2,
                "output_unigrams":"true"
        },
        "min_stemmer": {
            "type": "stemmer",
            "name": "minimal_english"
        },
    },
    "analyzer": {
        "nerd_text": {
            "char_filter": ["html_strip"],
            "tokenizer": "standard",
            "filter": ["lowercase", "stop", "asciifolding", "min_stemmer", "snowball"],
            "stopwords": "_english_"
        },
        "nerd_bigrams": {
            "char_filter": ["html_strip"],
            "tokenizer": "standard",
            "filter": ["lowercase",  "stop", "asciifolding", "min_stemmer", "bigram_filter"],
            "stopwords": "_english_"
        }
    }
}

settings = {
    "mappings": {
      "post": {
        "properties": {
            "Body": {
              "type": "string",
              "analyzer": "nerd_text",
              "fields": {
                "bigramed": {
                  "term_vector": "with_positions_offsets_payloads",
                  "type": "string",
                  "analyzer": "nerd_bigrams"
                }
              }
            },
            "Title": {
              "type": "string",
              "analyzer": "nerd_text",
              "fields": {
                "bigramed": {
                  "term_vector": "with_positions_offsets_payloads",
                  "type": "string",
                  "analyzer": "nerd_bigrams"
                }
              }
            }
        }
      }
    },
    "settings": {
      "index" : {
        "number_of_shards" : 1,
        "number_of_replicas" : 0,
        "analysis": analyzers
      },
    }
}

from elasticsearch import Elasticsearch, TransportError

try:
    es = Elasticsearch("http://localhost:9200")
    es.indices.delete(index='stackexchange', ignore=[400,404])
    es.indices.create(index='stackexchange', body=settings)
    es.indices.delete(index='stackexchange_munged', ignore=[400,404])
    es.indices.create(index='stackexchange_munged', body=settings)
    es.indices.delete(index='stackexchange_rand', ignore=[400,404])
    es.indices.create(index='stackexchange_rand', body=settings)
    es.indices.delete(index='stackexchange_grams', ignore=[400,404])
    es.indices.create(index='stackexchange_grams', body=settings)
except TransportError as e:
    print(repr(e))
