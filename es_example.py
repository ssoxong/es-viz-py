from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')
es.info()

def make_index(es, index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name)

index_name = 'goods'
doc1 = {'goods_name': '삼성 노트북 9',    'price': 1000000}
doc2 = {'goods_name': '엘지 노트북 그램', 'price': 2000000}
doc3 = {'goods_name': '애플 맥북 프로',   'price': 3000000}
doc4 = {'goods_name': '맥북',   'price': 100000}
doc5 = {'goods_name': '맥복',   'price': 100000}

make_index(es, index_name)

es.index(index=index_name, document=doc1)
es.index(index=index_name, document=doc2)
es.index(index=index_name, document=doc3)
es.index(index=index_name, document=doc4)
es.index(index=index_name, document=doc5)

es.indices.refresh(index=index_name)

results = es.search(index=index_name, body={'from': 0, 'size': 100, 'query': {'match': {'goods_name': '맥북'}}})
for result in results['hits']['hits']:
    print('score:', result['_score'], 'source:', result['_source'])
