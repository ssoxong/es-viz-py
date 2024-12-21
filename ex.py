from pecab import PeCab
import math
from elasticsearch import Elasticsearch
def get_documents_from_elasticsearch(es, index_name):
    """Elasticsearch에서 모든 문서를 가져오는 함수"""
    try:
        # 모든 문서를 가져오기 위한 scroll API 사용 (대량 문서 처리 효율적)
        docs = []
        scroll_response = es.search(index=index_name, scroll='1m', size=10000, body={"query": {"match_all": {}}}) # match_all 쿼리로 모든 문서 가져오기
        scroll_id = scroll_response['_scroll_id']
        docs.extend([hit['_source']['content'] for hit in scroll_response['hits']['hits']])

        while len(scroll_response['hits']['hits']) > 0:
            scroll_response = es.scroll(scroll_id=scroll_id, scroll='1m')
            docs.extend([hit['_source']['content'] for hit in scroll_response['hits']['hits']])

        es.clear_scroll(scroll_id=scroll_id) # 스크롤 컨텍스트 해제
        return docs
    except Exception as e:
        print(f"Elasticsearch에서 문서 가져오기 오류: {e}")
        return None
def getDFListWithPecab(words):
    if not words:
        return {}

    try:
        pecab = PeCab()
        word_counts = {}

        # for word in words:
        pos = pecab.pos(words)

        for p in pos:
            if p[1] != "NNG": continue
            key = f"{p[0]}/{p[1]}"
            word_counts[key] = word_counts.get(key, 0) + 1

        return word_counts

    except Exception as e:
        print(f"DF 계산 중 오류 발생: {e}")
        return {}


def getIDFListWithPecab(words):
    if not words:
        return {}

    try:
        word_counts = getDFListWithPecab(words)
        if not word_counts: # DF 계산에서 오류 발생 시 빈 딕셔너리 반환
          return {}

        total_words = sum(word_counts.values()) # 전체 단어 수 계산

        idf_list = {}
        for key, count in word_counts.items():
            idf = math.log(total_words / count)
            idf_list[key] = idf

        return idf_list

    except Exception as e:
        print(f"IDF 계산 중 오류 발생: {e}")
        return {}

# 테스트 코드
es = Elasticsearch(
    "http://localhost:9200"
)
index_name = "document_list" # 인덱스 이름 변경

# Elasticsearch에서 문서 가져오기
documents = get_documents_from_elasticsearch(es, index_name)

if documents is None:
    print("문서 목록을 가져오는데 실패했습니다. 프로그램을 종료합니다.")
    exit()

if not documents:
    print("인덱스에 문서가 없습니다.")
else:
    for doc in documents:
        print('-'*50)
        print('문서:', doc)
        idfList = getIDFListWithPecab(doc)
        print(sorted(idfList.items(), key=lambda x: x[1], reverse=True))

    # df_list = getDFListWithPecab(documents)
    # print("DF 결과:", df_list)

    # idf_list = getIDFListWithPecab(documents)
    # print("IDF 결과:", idf_list)
    # print('-'*50)
    # print(sorted(idf_list.items(), key=lambda x: x[1], reverse=True))
    pecab = PeCab()
    # print(pecab.pos("컴퓨터 비전 기술은 자율 주행, 로봇 공학 등 다양한 분야의 발전에 기여할 것으로 기대됩니다."))