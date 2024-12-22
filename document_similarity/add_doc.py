# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch, helpers

# Elasticsearch 클라이언트 초기화
es = Elasticsearch('http://localhost:9200')


content = """
1. 프로젝트 개요
1.1 프로젝트 배경
 손으로 글씨를 쓰는 행위는 아동기 집중력을 향상시키고 육체적 발달에 지대한 영향을 미치는 과정으로, 초등학교에서는 받아쓰기를 통해 글쓰기 학습을 도모해왔다. 그러나 최근 받아쓰기를 아동학대로 간주하는 항의가 발생하고 있어 학교에서 받아쓰기 교육을 꺼리는 실정이 되었다. 
 이에 더해, 주요 학습 매체가 책에서 전자기기로 대체되며 학생들이 손으로 글을 쓰는 빈도는 점차 줄고 있다. 전자기기의 특성상, 학생들은 화면을 짧게 두드리는 탭(Tap)과 키보드로 문자를 쓰는 타이핑(Typing)을 활용해 학습하는 경우가 대부분이다. 특히 '알파 세대'로 지칭되는 현재 초등학생들은 연필보다 스마트 기기가 더 익숙한 세대가 되었다. 
 받아쓰기는 집중력 향상과 육체 발달뿐만 아니라 새로운 어휘를 학습하고, 문장의 구조와 맞춤법을 점검할 수 있으므로 학생들은 지속적인 받아쓰기 연습이 필요하다. 따라서 교내외에서 손으로 글씨를 쓰며 받아쓰기 연습을 수행할 수 있도록 도움을 주는 프로그램이 요구된다.
 아이스크림 홈런, 소중한글 등 기존의 받아쓰기 학습 애플리케이션들은 기등록된 받 아쓰기 문제만 제공하므로 학습자 별로 맞춤형 문제를 제공하는 데 한계가 있으며, 답안을 통하여 학습자의 취약점을 분석하고 이를 개선할 수 있는 맞춤형 피드백을 제공하기 어렵다.
 서경희[7]에 따르면 초등학생 4-5학년 학생들의 받아쓰기를 음운규칙 유형별로 분류하여 살펴본 결과, 아동들은 받아쓰기에서 구개음화, 연음화, 경음화, 유음화, 비음화, 음운규칙 없음, 겹받침 쓰기, 기식음화 순으로 오류율이 높은 것으로 나타났다. 이는 아동들이 특정 음운 규칙에서 어려움을 겪고 있음을 의미한다. 따라서 효과적으로 학생들의 받아쓰기 실력을 향상시키기 위해서는 음운 규칙 유형별로 문제를 자동 생성하고 개별 맞춤형 학습을 제공해야 한다.
1.2 프로젝트 최종 목표
 본 프로젝트에서는 인공지능 기반 음운규칙 유형별 받아쓰기 학습 웹 서비스 ‘한글바다’를 구현한다. 
1.2.1 1차 목표: 한글바다 프로토타입 (24.03~24.06)
-	클래스: 교사(학부모)는 클래스를 생성하여 학생(자녀)를 참여하게 한다. 클래스에 속한 학생들의 점수를 한 눈에 확인할 수 있다.
-	문제집 및 문제 생성: 교사(학부모)는 문제집을 생성하여 받아쓰기 문제를 입력한다. 문제 및 문제집은 교사의 다른 클래스에서도 재사용 할 수 있다.
-	문제 풀기: 학생(자녀)는 받아쓰기 문제를 풀고, 답안 사진을 촬영하여 제출한다.
-	OCR을 활용한 문제 채점: 학생(자녀)의 답안을 인공지능 OCR 기술을 통해 텍스트 추출하고, 채점한다. 시중 받아쓰기 서비스와와 달리 전용 기기 없이 학습할 수 있다.
1.2.2 2차 목표: 한글바다 최종 - 음운 규칙 유형별 받아쓰기 (24.09~24.12)
-	음운규칙 유형별 받아쓰기 문제 자동 생성: 구개음화, 비음화 등과 같은 음운규칙 유형별로 맞춤형 받아쓰기 문제를 자동 생성한다.
-	받아쓰기 문장 난이도 자동 계산: 받아쓰기 문장에 사용된 음운규칙의 부분의 모음, 받침과 문장 길이를 고려하여 난이도를 자동으로 계산하여 맞춤형 학습을 제공한다. 
-	문제와 답안 유사도 측정을 통한 오답 유형 분석: 문제와 답안의 유사도를 측정하여 취약한 받아쓰기 문제 유형과 형태소를 분석하여 제공한다.
-	받아쓰기 특화된 인공지능 OCR 모델: 초중고 학생의 손글씨 데이터를 학습시킨 받아쓰기 전용 인공지능 OCR 모델을 개발하여 받아쓰기 답안 인식 정확률을 높인다.
-	문제집 공유: 교사들간 문제집을 공유할 수 있다.

2.4.2 맞춤형 학습을 위한 받아쓰기 문장 자동 난이도 계산
  김화영(2007) 연구결과에 따라 받침 자음과 모음에 대해 난이도 등급을 매긴 후([그림 2-1]), 받아쓰기 문장에서 음운규칙이 적용된 부분의 받침과 모음을 분석하여 문장의 난이도를 자동으로 계산한다. 추가적으로 문장의 길이도 고려하여 난이도를 조정한다.
2.4.3 문제와 답안 유사도 측정을 통한 오답 유형 분석
  받아쓰기 문제와 OCR로 인식된 답안의 유사도를 측정하여 오답 정도를 점수로 제공하고, 학습자별로 취약한 음운규칙 유형과 형태소를 분석한다. 추가적으로 오답노트를 통해 취약한 유형의 받아쓰기를 재학습할 수 있도록 한다.
2.4.4 손글씨로 채점받는 받아쓰기 학습
  본 프로젝트는 종이와 펜으로 받아쓰기를 한 후, 휴대폰과 같은 기기를 통해 답안을 업로드할 수 있어 홈런북 등과 같은 전용 디지털 기기를 구매할 필요가 없다. 또한 학생이 직접 손글씨로 받아쓰기를 하면서도 앱을 통해 자동 채점과 피드백을 받을 수 있다. 이를 통해 학생은 익숙한 태블릿이나 키보드를 통한 글쓰기에서 벗어나 종이에 글을 적으며 맞춤법과 글씨체를 점검할 수 있다.
2.4.5 받아쓰기 전용 인공지능 OCR 모델
  본 프로젝트에서는 손글씨에 특화된 받아쓰기 인공지능 OCR 모델을 개발하여 받아쓰기 답안의 인식 정확도를 향상시킨다. 초등학생부터 고등학생까지 학생들의 손글씨 데이터를 기반으로 인공지능 OCR 모델을 학습시켜, 일반적인 인공지능 OCR 모델에 비해 손글씨 인식률이 높은 모델을 개발한다. 이를 통해 ‘한글바다’ 서비스 내 받아쓰기 답안을 정확하게 인식할 수 있도록 한다. """

# 문서 리스트
doc = [
    {
        "_index": "document_sim_v2",
        "_source": {
            "title": "인공지능 기반 음운규칙 유형별 받아쓰기 학습 웹 서비스",
            "author": "이소현",
            "content": content
        }
    }
]
# Bulk API로 문서 색인
helpers.bulk(es, doc)

print("텍스트 색인 완료")