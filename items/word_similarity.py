"""
FastText 기반 한국어 단어 유사도 계산 서비스

꼬맨틀(Semantle-ko)과 동일한 방식으로 FastText 임베딩을 사용하여
아이템 이름 간의 의미적 유사도를 계산합니다.
"""

import os
import json
import numpy as np
from functools import lru_cache

# FastText 모델 경로 (한국어 모델)
# 다운로드: https://fasttext.cc/docs/en/crawl-vectors.html
# cc.ko.300.bin (약 4GB) 또는 cc.ko.300.vec (텍스트 형식)
FASTTEXT_MODEL_PATH = os.environ.get('FASTTEXT_MODEL_PATH', 'cc.ko.300.bin')

# 사전 계산된 유사도 매트릭스 (모델 없을 때 fallback)
PRECOMPUTED_SIMILARITY_PATH = os.path.join(os.path.dirname(__file__), 'item_similarity_matrix.json')

# 자주 사용되는 아이템 키워드 목록
ITEM_KEYWORDS = [
    # 액세서리
    '반지', '목걸이', '팔찌', '귀걸이', '브로치', '헤어핀', '머리끈',
    '시계', '손목시계', '스마트워치',
    # 키링/열쇠고리
    '키링', '열쇠고리', '키홀더', '참', '펜던트',
    # 가방류
    '가방', '백', '파우치', '지갑', '카드지갑', '명함지갑',
    '토트백', '숄더백', '크로스백', '클러치', '에코백',
    # 인형/피규어
    '인형', '피규어', '봉제인형', '캐릭터', '마스코트',
    # 전자기기
    '이어폰', '헤드폰', '에어팟', '버즈', '케이스', '폰케이스',
    '충전기', 'USB', '보조배터리', '태블릿',
    # 패션소품
    '스카프', '머플러', '모자', '캡', '비니', '장갑', '양말',
    '선글라스', '안경', '벨트', '넥타이',
    # 필기구/문구
    '펜', '만년필', '볼펜', '연필', '샤프', '형광펜',
    '다이어리', '노트', '스티커', '마스킹테이프',
    # 생활용품
    '텀블러', '머그컵', '컵', '물병', '보틀',
    '손거울', '거울', '빗', '화장품', '립밤', '핸드크림',
    # 취미용품
    '카메라', '책', '앨범', '달력', '포스터',
    # 식품 관련
    '초콜릿', '사탕', '젤리', '과자', '음료',
    # 꽃/식물
    '꽃', '화분', '식물', '선인장', '다육이',
    # 기타
    '우산', '손수건', '타올', '쿠션', '베개', '담요',
]


class WordSimilarityService:
    """단어 의미 유사도 계산 서비스"""

    _instance = None
    _model = None
    _precomputed = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._precomputed is None:
            self._load_precomputed()

    def _load_precomputed(self):
        """사전 계산된 유사도 매트릭스 로드"""
        try:
            if os.path.exists(PRECOMPUTED_SIMILARITY_PATH):
                with open(PRECOMPUTED_SIMILARITY_PATH, 'r', encoding='utf-8') as f:
                    self._precomputed = json.load(f)
                print(f"[WordSimilarity] Precomputed matrix loaded: {len(self._precomputed.get('words', []))} words")
            else:
                self._precomputed = {'words': [], 'matrix': {}, 'synonyms': {}}
                print("[WordSimilarity] No precomputed matrix found, using fallback")
        except Exception as e:
            print(f"[WordSimilarity] Error loading precomputed: {e}")
            self._precomputed = {'words': [], 'matrix': {}, 'synonyms': {}}

    def _load_fasttext_model(self):
        """FastText 모델 로드 (선택적)"""
        if self._model is not None:
            return True

        try:
            import fasttext
            if os.path.exists(FASTTEXT_MODEL_PATH):
                self._model = fasttext.load_model(FASTTEXT_MODEL_PATH)
                print(f"[WordSimilarity] FastText model loaded from {FASTTEXT_MODEL_PATH}")
                return True
        except ImportError:
            print("[WordSimilarity] fasttext not installed, using precomputed only")
        except Exception as e:
            print(f"[WordSimilarity] Error loading FastText: {e}")

        return False

    @lru_cache(maxsize=1000)
    def get_similarity(self, word1: str, word2: str) -> float:
        """
        두 단어의 의미적 유사도 계산 (0.0 ~ 1.0)

        1순위: 사전 계산된 매트릭스
        2순위: FastText 모델 (있으면)
        3순위: 문자열 유사도 fallback
        """
        # 정규화
        word1 = word1.strip().lower() if word1 else ''
        word2 = word2.strip().lower() if word2 else ''

        if not word1 or not word2:
            return 0.0

        if word1 == word2:
            return 1.0

        # 동의어 체크
        synonyms = self._precomputed.get('synonyms', {})
        if word1 in synonyms.get(word2, []) or word2 in synonyms.get(word1, []):
            return 0.95

        # 1. 사전 계산된 매트릭스에서 검색
        matrix = self._precomputed.get('matrix', {})
        key1 = f"{word1}:{word2}"
        key2 = f"{word2}:{word1}"

        if key1 in matrix:
            return matrix[key1]
        if key2 in matrix:
            return matrix[key2]

        # 2. 부분 매칭 (포함 관계)
        if word1 in word2 or word2 in word1:
            return 0.7

        # 3. 카테고리 기반 유사도
        category_sim = self._get_category_similarity(word1, word2)
        if category_sim > 0:
            return category_sim

        # 4. 문자열 유사도 (Jaro-Winkler)
        return self._string_similarity(word1, word2) * 0.5  # 최대 0.5점

    def _get_category_similarity(self, word1: str, word2: str) -> float:
        """카테고리 기반 유사도"""
        categories = {
            '액세서리': ['반지', '목걸이', '팔찌', '귀걸이', '브로치', '헤어핀', '시계', '펜던트'],
            '키링류': ['키링', '열쇠고리', '키홀더', '참', '스트랩'],
            '가방류': ['가방', '백', '파우치', '지갑', '토트백', '숄더백', '크로스백', '클러치'],
            '전자기기': ['이어폰', '헤드폰', '에어팟', '버즈', '충전기', '케이스'],
            '패션소품': ['스카프', '머플러', '모자', '캡', '비니', '장갑', '선글라스', '안경'],
            '문구류': ['펜', '만년필', '볼펜', '다이어리', '노트', '스티커'],
            '인형류': ['인형', '피규어', '봉제인형', '캐릭터', '마스코트'],
            '음료용품': ['텀블러', '머그컵', '컵', '물병', '보틀'],
        }

        word1_cat = None
        word2_cat = None

        for cat, keywords in categories.items():
            for kw in keywords:
                if kw in word1:
                    word1_cat = cat
                if kw in word2:
                    word2_cat = cat

        if word1_cat and word2_cat:
            if word1_cat == word2_cat:
                return 0.6  # 같은 카테고리
            else:
                return 0.2  # 다른 카테고리지만 아이템

        return 0.0

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Jaro-Winkler 문자열 유사도"""
        if not s1 or not s2:
            return 0.0

        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0

        match_distance = max(len1, len2) // 2 - 1
        if match_distance < 0:
            match_distance = 0

        s1_matches = [False] * len1
        s2_matches = [False] * len2

        matches = 0
        transpositions = 0

        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len2)

            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        jaro = (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3

        # Winkler 수정
        prefix = 0
        for i in range(min(len1, len2, 4)):
            if s1[i] == s2[i]:
                prefix += 1
            else:
                break

        return jaro + prefix * 0.1 * (1 - jaro)

    def get_max_similarity(self, item_name: str, lucky_items: list) -> tuple:
        """
        아이템 이름과 행운 아이템 목록 중 가장 높은 유사도 반환

        Returns:
            (max_similarity, best_match_item)
        """
        if not item_name or not lucky_items:
            return 0.0, None

        max_sim = 0.0
        best_match = None

        # 아이템 이름에서 주요 단어 추출
        item_words = self._extract_keywords(item_name)

        for lucky_item in lucky_items:
            if not lucky_item:
                continue

            lucky_words = self._extract_keywords(lucky_item)

            # 각 단어 쌍의 최대 유사도
            for iw in item_words:
                for lw in lucky_words:
                    sim = self.get_similarity(iw, lw)
                    if sim > max_sim:
                        max_sim = sim
                        best_match = lucky_item

        return max_sim, best_match

    def _extract_keywords(self, text: str) -> list:
        """텍스트에서 키워드 추출"""
        if not text:
            return []

        # 공백, 특수문자로 분리
        import re
        words = re.split(r'[\s,_\-/]+', text)

        # 빈 문자열 제거 및 2글자 이상만
        keywords = [w.strip() for w in words if w.strip() and len(w.strip()) >= 2]

        # 원본 텍스트도 포함
        if text.strip() and text.strip() not in keywords:
            keywords.append(text.strip())

        return keywords


# 사전 계산된 유사도 매트릭스 생성 스크립트
def generate_similarity_matrix():
    """
    FastText 모델을 사용하여 아이템 키워드 간 유사도 매트릭스 생성
    이 함수는 개발 시 한 번 실행하여 JSON 파일로 저장합니다.
    """
    try:
        import fasttext
    except ImportError:
        print("fasttext 패키지를 설치해주세요: pip install fasttext")
        return

    model_path = FASTTEXT_MODEL_PATH
    if not os.path.exists(model_path):
        print(f"FastText 모델을 다운로드해주세요: {model_path}")
        print("다운로드 링크: https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.ko.300.bin.gz")
        return

    print("FastText 모델 로딩 중...")
    model = fasttext.load_model(model_path)

    # 유사도 매트릭스 계산
    matrix = {}
    words = ITEM_KEYWORDS

    print(f"유사도 계산 중... ({len(words)}개 단어)")
    for i, w1 in enumerate(words):
        for w2 in words[i+1:]:
            # FastText 코사인 유사도
            vec1 = model.get_word_vector(w1)
            vec2 = model.get_word_vector(w2)

            # 코사인 유사도
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

            # 0.3 이상인 것만 저장 (의미 있는 유사도)
            if similarity >= 0.3:
                matrix[f"{w1}:{w2}"] = round(float(similarity), 3)

    # 동의어 목록
    synonyms = {
        '키링': ['열쇠고리', '키홀더'],
        '열쇠고리': ['키링', '키홀더'],
        '키홀더': ['키링', '열쇠고리'],
        '가방': ['백', '파우치'],
        '백': ['가방', '파우치'],
        '이어폰': ['헤드폰', '에어팟', '버즈'],
        '헤드폰': ['이어폰'],
        '인형': ['봉제인형', '피규어'],
        '봉제인형': ['인형'],
        '텀블러': ['머그컵', '컵', '물병'],
        '머그컵': ['텀블러', '컵'],
        '펜': ['볼펜', '만년필'],
        '볼펜': ['펜', '만년필'],
        '만년필': ['펜', '볼펜'],
    }

    result = {
        'words': words,
        'matrix': matrix,
        'synonyms': synonyms,
        'version': '1.0'
    }

    # JSON 저장
    output_path = PRECOMPUTED_SIMILARITY_PATH
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"유사도 매트릭스 저장 완료: {output_path}")
    print(f"총 {len(matrix)}개의 유사도 쌍 저장됨")


# 싱글톤 인스턴스
_service = None

def get_word_similarity_service() -> WordSimilarityService:
    global _service
    if _service is None:
        _service = WordSimilarityService()
    return _service


if __name__ == '__main__':
    # 개발용: 유사도 매트릭스 생성
    generate_similarity_matrix()