from elasticsearch import Elasticsearch

ELASTICSEARCH_URL = "http://localhost:9200"


def query_elasticsearch():
    es = Elasticsearch(ELASTICSEARCH_URL)

    # Send test message
    doc = {
        "author": "Bia",
        "text": "Sending message from command line",
    }
    resp = es.index(index="messages", id="1", document=doc)
    print(resp["result"])

    resp = es.get(index="messages", id="1")
    print(resp["_source"])

    es.indices.refresh(index="messages")

    resp = es.search(index="messages")
    print("\nGot %d Hits!\n" % resp["hits"]["total"]["value"])
    for hit in resp["hits"]["hits"][:3]:
        print(hit["_source"])


if __name__ == "__main__":
    query_elasticsearch()
