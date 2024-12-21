from elasticsearch import Elasticsearch
from pecab import PeCab
import numpy as np
from collections import defaultdict
import math

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200"
)

def text_to_vector(text, idf_dict, vector_size=100):
    """텍스트를 벡터로 변환"""
    pecab = PeCab()
    words = pecab.nouns(text)
    
    # TF 계산
    tf_dict = defaultdict(float)
    for word in words:
        tf_dict[word] += 1.0
    
    # TF-IDF 계산
    tfidf_dict = {}
    for word, tf in tf_dict.items():
        if word in idf_dict:
            tfidf_dict[word] = tf * idf_dict[word]
    
    # 벡터 생성 (모든 값이 0이 되는 것을 방지)
    if not tfidf_dict:  # 만약 매칭되는 단어가 없다면
        vector = np.random.uniform(0.1, 0.2, vector_size)  # 작은 랜덤값으로 초기화
    else:
        vector = np.zeros(vector_size)
        sorted_words = sorted(tfidf_dict.items(), key=lambda x: x[1], reverse=True)
        
        # 벡터 채우기
        for i, (word, tfidf) in enumerate(sorted_words):
            if i < vector_size:
                vector[i] = max(tfidf, 0.1)  # 최소값 보장
            else:
                break
        
        # 벡터 정규화
        magnitude = np.linalg.norm(vector)
        if magnitude > 0:
            vector = vector / magnitude
    # print(vector)
    return vector.tolist()

def create_test_documents():
    """테스트용 문서 생성"""
    test_docs = [
        "청소년 상담 프로그램 개발에 관한 연구",
        "인공지능 기술의 발전과 미래 전망",
        "데이터 분석을 통한 교육 효과 분석",
        "스마트폰 사용이 청소년에 미치는 영향",
        "효과적인 학습 방법에 대한 연구"
    ]
    
    for doc in test_docs:
        vector = text_to_vector(doc, idf_dict)
        doc_body = {
            "content": doc,
            "doc_vector": vector
        }
        es.index(index=index_name, body=doc_body)
        print(f"Indexed: {doc}")

def search_similar_documents(query_text, top_k=5):
    """유사 문서 검색"""
    query_vector = text_to_vector(query_text, idf_dict)
    
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'doc_vector') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }
    
    response = es.search(
        index=index_name,
        body={
            "query": script_query,
            "size": top_k
        }
    )
    
    return response['hits']['hits']
if __name__ == "__main__":
    index_name = "document_similarity"
    
    # 인덱스 매핑 정의
    mapping = {
        "mappings": {
            "properties": {
                "content": {"type": "text"},
                "doc_vector": {
                    "type": "dense_vector",
                    "dims": 100,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }

    # 기존 인덱스 삭제 후 새로 생성
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name, body=mapping)
    print("Index created successfully")

    # 초기 IDF 사전 생성 (테스트용 간단 버전)
    idf_dict = defaultdict(lambda: 1.0)  # 모든 단어에 대해 IDF=1로 시작
    
    # 테스트 문서 생성
    create_test_documents()
    print("\n문서 색인 완료")

    # 검색 테스트
    query = "청소년 상담 프로그램"
    results = search_similar_documents(query, top_k=3)

    print(f"\n검색어: {query}")
    print("-" * 80)
    print(results)
    for hit in results:
        print(f"Score: {hit['_score']}")
        print(f"Content: {hit['_source']['content']}")
        print("-" * 80)