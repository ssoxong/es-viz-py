from pecab import PeCab
import math
from elasticsearch import Elasticsearch
import numpy as np

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
    
def getTopWordListWithPecab(words):
    if not words:
        return []

    try:
        idf_list = getIDFListWithPecab(words)
        if not idf_list: # IDF 계산에서 오류 발생 시 빈 리스트 반환
            return []

        return sorted(idf_list.keys(), key=lambda x: x[1], reverse=True)

    except Exception as e:
        print(f"상위 단어 목록 추출 중 오류 발생: {e}")
        return []
    

def makeVector(words):
    import gensim
    model = gensim.models.Word2Vec.load('D:\document_similarity\data\ko.bin')

    WORD_VECTOR_DIM = model.wv.vector_size # 모델로부터 벡터 차원 추출

    topWordList = getTopWordListWithPecab(words)

    splitList = []
    for word in topWordList:
        splitList.append(word.split("/")[0])
    topWordList = splitList
    # topWordList가 비어있는 경우 처리
    if not topWordList:
        return np.zeros(WORD_VECTOR_DIM, dtype=float)

    vectors = []
    for word in topWordList:
        try:
            vectors.append(model.wv[word])
        except KeyError:
            print(f"Warning: Word '{word}' not found in vocabulary: {word}") #어떤 단어가 없는지 출력
            continue #모델에 없는 단어는 건너뜀

    if not vectors: #벡터가 하나도 없는경우 0벡터 반환
        return np.zeros(WORD_VECTOR_DIM, dtype=float)
    
    result = np.mean(vectors, axis=0)
    return result

def getConsineSimilarity(vec1, vec2):
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity([vec1], [vec2])

# 테스트 코드
es = Elasticsearch(
    "http://localhost:9200"
)
index_name = "document_sim_v2" # 인덱스 이름 변경

# Elasticsearch에서 문서 가져오기
# documents = get_documents_from_elasticsearch(es, index_name)
# print(documents)
# print('-'*50)
# print(getTopWordListWithPecab(dd['hits']['hits'][4]['_source']['content']))

# print(makeVector("강아지"))
print("강아지 고양이: ", getConsineSimilarity(makeVector("강아지"), makeVector("고양이")))
print("강아지 강아지: ", getConsineSimilarity(makeVector("강아지"), makeVector("강아지")))
print("강아지 짜장면: ", getConsineSimilarity(makeVector("강아지"), makeVector("짜장면")))

# result = es.search(index=index_name, body={
#     "query": {"match": {"title": "인공지능 기반 음운규칙 유형별 받아쓰기 학습 웹 서비스"}}})
# resultVector = makeVector(result["hits"]["hits"][0]["_source"]["content"])


# print(getTopWordListWithPecab(result["hits"]["hits"][0]["_source"]["content"]))
# print("학습: ", getConsineSimilarity(resultVector, makeVector("학습")))
# print("음식: ", getConsineSimilarity(resultVector, makeVector("음식")))


# 모든 도큐먼트에 대한 벡터 생성
# documents = es.search(index=index_name, body={"query": {"match_all": {}}})["hits"]["hits"]
# for doc in documents:
#     doc_id = doc["_id"]
#     resultVector = makeVector(doc["_source"]["content"])
#     # formatted_string = "["
#     # for i, num in enumerate(resultVector):
#     #     formatted_string += str(num)
#     #     if i < len(resultVector) - 1:
#     #         formatted_string += ", "
#     # formatted_string += "]"
#     print(es.update(index=index_name, id=doc_id, body={"doc": {"doc_vector": resultVector.tolist()}}))

# res = es.search(index=index_name, body={
#     "_source": ["title"],
#     "query": {
#     "knn": {
#         "field": "doc_vector", 
#         "query_vector": [0.11082647, -0.089203216, -0.45089233, 0.27369347, -0.26999417, 0.33410108, -1.0169702, 0.5258958, -0.3402772, 0.047811374, -0.038291246, -0.25384292, -0.13132548, -1.0175552, -0.2284314, 0.14049967, -0.44696584, 0.07671037, -0.053289354, -0.123693325, 0.35156122, 0.1328916, 0.4893403, 0.17548917, 0.5537532, -0.2961873, -0.5018577, -0.087624654, -0.25292453, -0.3326299, 0.12760696, 0.10159496, -0.013132876, 0.19041644, -0.23397262, 0.010215033, 0.18998106, -0.36745358, 0.5085219, 0.14937764, -0.089002274, -0.97228837, 0.37043825, 0.09067693, -0.31942087, 0.6041918, 0.28828594, -0.42385808, 0.04112876, -0.21520789, 0.21022762, 0.065987535, -0.15468074, -0.3253219, -0.24694806, -0.2603258, 0.15558575, -0.16076937, -0.26395786, -0.18739364, -0.10439225, 0.009360865, -0.28470105, 0.6632844, -0.6969602, 0.1751161, 0.092138834, 0.40253896, 0.03305878, 0.105711505, 0.4829989, -0.032497272, -0.38710877, -0.2607129, -0.1636851, -0.12690797, 0.11941233, 0.2873263, 0.4693776, -0.015706085, -0.30780154, -0.53484154, -0.046562567, -0.24973537, -0.9992988, -0.3599233, 0.104781955, 0.07329153, -0.5765212, 0.06776329, 0.59842694, -0.0529784, 0.8331423, 0.154535, 0.32728902, 0.6130296, 0.21352772, -0.53469366, 0.07700043, -0.25352392, -0.34538457, 0.057699047, 0.03594152, -0.46228564, 0.55375475, 0.5208228, -0.89891934, 0.5781123, 0.10645293, -0.6889079, 0.62326765, -0.7651265, 0.098112784, -0.4349575, -0.07734433, -0.55886894, -0.45950252, 0.212013, -0.1428302, -0.007001544, -0.30973136, -0.17974871, -0.3076331, -0.6176157, 0.08367294, 0.3930403, 0.5421897, -0.5015842, 0.48665518, 0.033152245, -0.088254, -0.48833936, 0.08922404, -0.11976029, -0.4856137, 0.9577622, 0.9177955, -0.029399546, 0.33669055, -0.12513328, -0.45105767, -0.2580463, -0.031247113, -0.13410707, -0.5290871, 0.07210006, 0.03607123, -0.2090809, -0.20082757, -0.64340836, -0.5710711, 0.052224338, -0.117592566, 0.104786165, -0.2590196, -0.81953067, 0.017096754, 0.44927517, 0.1337764, -0.5420108, -0.12418169, -0.17614909, -0.4425072, -0.7502179, -0.81210893, -0.14137128, 0.36322707, 0.20616439, -0.14723119, 0.6762307, 0.12409828, 0.0618407, -0.45664605, -0.43834278, 0.5023247, -0.09149563, -0.48899484, 0.68053746, 0.5766486, 0.09627072, 0.3872944, -0.17918581, 0.3929848, 0.004592324, 0.052833963, -0.057145722, 0.1274711, 0.2701624, 0.029962912, 0.39675415, -0.8669575, 0.0051424727, -0.16999969, -0.3326316, 0.19726147, 0.26913828, 0.13816915, 0.78223306, 0.052557044, -0.22202097],
#     }
#     }
# })
# for r in res['hits']['hits']:
#     print(r['_score'])
#     print(r['_source']['title'])

def searchDocSimilarity(word):
    result = es.search(index=index_name, body={
        "_source": ["title"],
        "query": {
        "knn": {
            "field": "doc_vector", 
            "query_vector": makeVector(word).tolist(),
        }
        }
    })
    return result

text = "불확실성을 이용한 기술"
res = searchDocSimilarity(text)
print("test: ", text)
for r in res['hits']['hits']:
    print(r['_score'])
    print(r['_source']['title'])