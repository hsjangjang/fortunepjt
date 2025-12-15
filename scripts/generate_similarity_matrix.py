"""
FastText 기반 아이템 키워드 유사도 매트릭스 생성 스크립트

사용법:
    python scripts/generate_similarity_matrix.py

출력:
    frontend/src/data/itemSimilarity.json
"""

import json
import numpy as np
from pathlib import Path

# FastText 모델 경로
FASTTEXT_VEC_PATH = r"C:\Users\HASUN\Desktop\cc.ko.300.vec"

# 출력 경로
OUTPUT_PATH = Path(__file__).parent.parent / "frontend" / "src" / "data" / "itemSimilarity.json"

# 아이템 관련 키워드 목록 (운세 서비스에서 사용되는 아이템들)
ITEM_KEYWORDS = [
    # 액세서리
    "반지", "목걸이", "팔찌", "귀걸이", "브로치", "헤어핀", "머리끈",
    "펜던트", "참", "뱅글", "링",
    # 시계
    "시계", "손목시계", "스마트워치",
    # 키링/열쇠고리
    "키링", "열쇠고리", "키홀더", "스트랩", "폰스트랩",
    # 가방류
    "가방", "백", "파우치", "지갑", "카드지갑",
    "토트백", "숄더백", "크로스백", "클러치", "에코백", "핸드백",
    # 인형/피규어
    "인형", "피규어", "봉제인형", "캐릭터", "마스코트",
    # 전자기기
    "이어폰", "헤드폰", "에어팟", "충전기", "케이스", "폰케이스", "보조배터리",
    # 패션소품
    "스카프", "머플러", "목도리", "숄",
    "모자", "캡", "비니",
    "장갑", "양말",
    "선글라스", "안경",
    "벨트", "넥타이",
    # 문구류
    "펜", "만년필", "볼펜", "연필",
    "다이어리", "노트", "스티커", "메모지", "필통",
    # 음료용품
    "텀블러", "머그컵", "컵", "물병", "보틀", "보온병",
    # 화장품류
    "립스틱", "립밤", "핸드크림", "향수", "로션",
    # 생활용품
    "손거울", "거울", "빗", "우산", "양산", "손수건", "타올",
    # 기타
    "책", "앨범", "사진", "꽃", "화분", "초콜릿", "사탕",
]


def load_fasttext_vectors(filepath: str, keywords: list) -> dict:
    """
    FastText .vec 파일에서 필요한 단어의 벡터만 로드
    """
    print(f"Loading FastText vectors from {filepath}...")
    print(f"Looking for {len(keywords)} keywords...")

    keyword_set = set(keywords)
    vectors = {}

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        # 첫 줄: 단어 수, 벡터 차원
        first_line = f.readline().strip().split()
        num_words, dim = int(first_line[0]), int(first_line[1])
        print(f"Model info: {num_words} words, {dim} dimensions")

        # 각 줄 읽기
        line_count = 0
        for line in f:
            line_count += 1
            if line_count % 500000 == 0:
                print(f"  Processed {line_count:,} lines, found {len(vectors)} keywords...")

            parts = line.rstrip().split(' ')
            word = parts[0]

            if word in keyword_set:
                try:
                    vector = np.array([float(x) for x in parts[1:]], dtype=np.float32)
                    if len(vector) == dim:
                        vectors[word] = vector
                        print(f"  Found: {word}")
                except ValueError:
                    continue

            # 모든 키워드를 찾으면 조기 종료
            if len(vectors) == len(keyword_set):
                break

    print(f"Loaded {len(vectors)} word vectors")
    return vectors


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """코사인 유사도 계산"""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))


def generate_similarity_matrix(vectors: dict) -> dict:
    """
    모든 키워드 쌍의 유사도 매트릭스 생성
    """
    print("\nGenerating similarity matrix...")

    words = list(vectors.keys())
    matrix = {}

    for i, word1 in enumerate(words):
        for word2 in words[i+1:]:
            sim = cosine_similarity(vectors[word1], vectors[word2])
            # 0.3 이상인 유사도만 저장 (의미 있는 관계)
            if sim >= 0.3:
                key = f"{word1}:{word2}"
                matrix[key] = round(sim, 4)

    print(f"Generated {len(matrix)} similarity pairs")
    return matrix, words


def create_category_mapping(found_words: list) -> dict:
    """카테고리별 키워드 매핑 생성"""
    categories = {
        "액세서리": ["반지", "목걸이", "팔찌", "귀걸이", "브로치", "헤어핀", "머리끈", "펜던트", "참", "뱅글", "링"],
        "시계류": ["시계", "손목시계", "스마트워치"],
        "키링류": ["키링", "열쇠고리", "키홀더", "스트랩", "폰스트랩"],
        "가방류": ["가방", "백", "파우치", "지갑", "카드지갑", "토트백", "숄더백", "크로스백", "클러치", "에코백", "핸드백"],
        "인형류": ["인형", "피규어", "봉제인형", "캐릭터", "마스코트"],
        "전자기기": ["이어폰", "헤드폰", "에어팟", "충전기", "케이스", "폰케이스", "보조배터리"],
        "패션소품": ["스카프", "머플러", "목도리", "숄", "모자", "캡", "비니", "장갑", "양말", "선글라스", "안경", "벨트", "넥타이"],
        "문구류": ["펜", "만년필", "볼펜", "연필", "다이어리", "노트", "스티커", "메모지", "필통"],
        "음료용품": ["텀블러", "머그컵", "컵", "물병", "보틀", "보온병"],
        "화장품류": ["립스틱", "립밤", "핸드크림", "향수", "로션"],
        "생활용품": ["손거울", "거울", "빗", "우산", "양산", "손수건", "타올"],
    }

    # 실제로 찾은 단어만 포함
    found_set = set(found_words)
    filtered_categories = {}
    for cat, words in categories.items():
        filtered = [w for w in words if w in found_set]
        if filtered:
            filtered_categories[cat] = filtered

    return filtered_categories


def create_synonyms_mapping() -> dict:
    """동의어 매핑 생성 (유사도 0.9 이상으로 처리할 단어들)"""
    return {
        "키링": ["열쇠고리", "키홀더"],
        "열쇠고리": ["키링", "키홀더"],
        "키홀더": ["키링", "열쇠고리"],
        "가방": ["백"],
        "백": ["가방"],
        "스카프": ["머플러", "목도리"],
        "머플러": ["스카프", "목도리"],
        "목도리": ["스카프", "머플러"],
        "모자": ["캡", "비니"],
        "텀블러": ["보온병"],
        "보온병": ["텀블러"],
        "펜": ["볼펜", "만년필"],
        "볼펜": ["펜"],
        "만년필": ["펜"],
        "손거울": ["거울"],
        "거울": ["손거울"],
        "우산": ["양산"],
        "양산": ["우산"],
    }


def main():
    # 1. FastText 벡터 로드
    vectors = load_fasttext_vectors(FASTTEXT_VEC_PATH, ITEM_KEYWORDS)

    if not vectors:
        print("Error: No vectors loaded!")
        return

    # 2. 유사도 매트릭스 생성
    matrix, found_words = generate_similarity_matrix(vectors)

    # 3. 카테고리 매핑 생성
    categories = create_category_mapping(found_words)

    # 4. 동의어 매핑
    synonyms = create_synonyms_mapping()

    # 5. 결과 JSON 생성
    result = {
        "version": "1.0",
        "description": "FastText (cc.ko.300) 기반 아이템 키워드 의미적 유사도",
        "model": "cc.ko.300.vec",
        "words": found_words,
        "categories": categories,
        "synonyms": synonyms,
        "matrix": matrix
    }

    # 6. 출력 디렉토리 생성
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 7. JSON 저장
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved to {OUTPUT_PATH}")
    print(f"   - {len(found_words)} words")
    print(f"   - {len(matrix)} similarity pairs")
    print(f"   - {len(categories)} categories")

    # 8. 샘플 출력
    print("\n📊 Sample similarities:")
    sample_pairs = [
        ("반지", "목걸이"),
        ("키링", "열쇠고리"),
        ("가방", "지갑"),
        ("인형", "피규어"),
        ("펜", "볼펜"),
    ]
    for w1, w2 in sample_pairs:
        key1, key2 = f"{w1}:{w2}", f"{w2}:{w1}"
        sim = matrix.get(key1) or matrix.get(key2) or "N/A"
        print(f"   {w1} <-> {w2}: {sim}")


if __name__ == "__main__":
    main()