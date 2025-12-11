"""
운세 계산 핵심 로직
"""
from datetime import date, datetime
import random
import hashlib
import json
from typing import Dict, List, Optional
from django.core.cache import cache
from django.conf import settings
from .saju_calculator import SajuCalculator
from .lunar_converter import lunar_to_solar

class FortuneCalculator:
    """운세 계산 클래스"""
    
    # 색상 코드와 이름 매핑
    COLOR_NAMES = {
        '#FF0000': '빨간색',
        '#FF6347': '토마토색',
        '#FFA500': '주황색',
        '#FFB347': '밝은 주황색',
        '#FFFF00': '노란색',
        '#F0E68C': '카키색',
        '#228B22': '초록색',
        '#32CD32': '연두색',
        '#90EE90': '연한 초록색',
        '#00FF00': '라임색',
        '#008000': '진초록색',
        '#0000FF': '파란색',
        '#000080': '남색',
        '#87CEEB': '하늘색',
        '#4169E1': '로열블루',
        '#800080': '보라색',
        '#DA70D6': '연보라색',
        '#FFC0CB': '분홍색',
        '#FFB6C1': '연분홍색',
        '#FFFFFF': '흰색',
        '#000000': '검은색',
        '#808080': '회색',
        '#C0C0C0': '은색',
        '#FFD700': '금색',
        '#D2691E': '갈색',
        '#8B4513': '진갈색',
        '#DEB887': '연갈색',
        '#F5DEB3': '베이지색',
    }
    
    # 색상 이름 -> HEX 매핑 (역방향)
    NAME_TO_HEX = {name: hex_code for hex_code, name in COLOR_NAMES.items()}
    
    # 별자리별 행운색 (기본 색상 풀)
    STAR_SIGN_COLORS = {
        '양자리': ['빨간색', '주황색', '흰색', '금색', '분홍색'],
        '황소자리': ['초록색', '분홍색', '베이지색', '갈색', '연두색'],
        '쌍둥이자리': ['노란색', '은색', '하늘색', '연보라색', '흰색'],
        '게자리': ['흰색', '은색', '연보라색', '하늘색', '분홍색'],
        '사자자리': ['금색', '주황색', '빨간색', '노란색', '흰색'],
        '처녀자리': ['남색', '회색', '베이지색', '초록색', '흰색'],
        '천칭자리': ['분홍색', '하늘색', '연보라색', '베이지색', '흰색'],
        '전갈자리': ['진한 빨간색', '검은색', '보라색', '남색', '금색'],
        '사수자리': ['보라색', '남색', '주황색', '빨간색', '금색'],
        '염소자리': ['갈색', '검은색', '회색', '남색', '베이지색'],
        '물병자리': ['하늘색', '파란색', '은색', '연보라색', '흰색'],
        '물고기자리': ['연보라색', '연두색', '분홍색', '하늘색', '은색']
    }

    # 띠별 행운색
    CHINESE_ZODIAC_COLORS = {
        '쥐띠': ['파란색', '금색', '초록색'],
        '소띠': ['흰색', '노란색', '초록색'],
        '호랑이띠': ['파란색', '회색', '주황색'],
        '토끼띠': ['분홍색', '연보라색', '빨간색'],
        '용띠': ['금색', '은색', '회색'],
        '뱀띠': ['빨간색', '노란색', '검은색'],
        '말띠': ['노란색', '초록색', '빨간색'],
        '양띠': ['초록색', '빨간색', '연보라색'],
        '원숭이띠': ['흰색', '금색', '하늘색'],
        '닭띠': ['금색', '갈색', '노란색'],
        '개띠': ['초록색', '빨간색', '연보라색'],
        '돼지띠': ['노란색', '회색', '갈색']
    }

    # 전체 색상 풀 (랜덤 보완용)
    ALL_COLORS = [
        '빨간색', '주황색', '노란색', '초록색', '연두색',
        '파란색', '하늘색', '남색', '보라색', '연보라색',
        '분홍색', '흰색', '검은색', '회색', '은색',
        '금색', '갈색', '베이지색', '진한 빨간색'
    ]
    
    # def __init__(self):
    #     self.cache_ttl = getattr(settings, 'CACHE_TTL', 86400)  # 24시간
    def __init__(self):
        self.cache_ttl = getattr(settings, 'CACHE_TTL', 86400)
        self.saju_calc = SajuCalculator()  # 이 줄 추가
    
    def calculate_fortune(
        self,
        birth_date: date,
        gender: str,
        birth_time: Optional[datetime] = None,
        chinese_name: Optional[str] = None,
        mbti: Optional[str] = None,  # MBTI 추가
        calendar_type: str = 'solar',  # 양력/음력 구분 (기본값: 양력)
        user_id: Optional[int] = None,  # 로그인 사용자 ID (로또 번호용)
        session_key: Optional[str] = None  # 세션 키 (비로그인 사용자 로또 번호용)
    ) -> Dict:
        """
        운세 계산 메인 함수
        """
        # 음력인 경우 양력으로 변환
        original_birth_date = birth_date  # 원본 음력 날짜 보관 (띠 계산용)
        if calendar_type == 'lunar':
            solar_date = lunar_to_solar(birth_date)
            if solar_date:
                birth_date = solar_date  # 양력으로 변환된 날짜 사용
                print(f"[DEBUG] 음력 {original_birth_date} -> 양력 {birth_date} 변환")
            else:
                print(f"[WARNING] 음력 변환 실패, 원본 날짜 사용")

        # 오늘 날짜
        today = date.today()

        # 고유 시드 생성 (날짜 + 생년월일로 매일 같은 운세 보장)
        seed_string = f"{today.isoformat()}-{birth_date.isoformat()}-{gender}"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
        random.seed(seed)

        # 사주 데이터 계산 (운세 점수 계산에 필요하므로 먼저 계산)
        saju_data = self._calculate_saju(birth_date, birth_time)

        # 각 운별 점수 계산 (사주 오행 데이터 반영)
        fortune_scores = self._calculate_all_fortunes(birth_date, today, saju_data)
        
        # 별자리 계산 (양력 날짜로)
        zodiac_sign = self._get_zodiac_sign(birth_date)

        # 띠 계산
        # 음력인 경우: 원본 음력 날짜의 년도로 띠 계산 (음력 설날 기준)
        # 양력인 경우: 입춘 기준으로 띠 계산
        if calendar_type == 'lunar':
            # 음력은 년도만 사용 (음력 1월 1일이 설날 = 띠가 바뀌는 날)
            chinese_zodiac = self._get_chinese_zodiac_lunar(original_birth_date)
        else:
            # 양력은 입춘 기준
            chinese_zodiac = self._get_chinese_zodiac(birth_date)
        
        # 행운의 색상들 결정 (별자리 + 띠 + 날짜 + 운세점수 기반)
        lucky_colors = self._determine_lucky_colors(
            zodiac_sign, chinese_zodiac, today, fortune_scores
        )

        # 로또 번호 6개 생성 (user_id 또는 session_key 기반으로 사용자별 다른 번호)
        lotto_numbers = self._generate_lucky_lotto_numbers(
            birth_date, today, fortune_scores, gender, user_id, session_key
        )
        
        # 행운의 아이템 (user_id 기반으로 사용자별 일관된 아이템, 가장 낮은 운 보완 기반)
        lucky_item = self._determine_lucky_item(
            zodiac_sign, today, user_id, session_key, lucky_colors,
            fortune_score=fortune_scores['total'],
            fortune_scores=fortune_scores
        )

        # 상세 운세 텍스트 생성 (LLM 시도 후 실패시 기존 로직)
        fortune_texts = self._generate_fortune_text_with_llm(
            birth_date, gender, saju_data, zodiac_sign, chinese_zodiac, fortune_scores, mbti,
            lucky_item['main'], lucky_item['zodiac']
        )

        if fortune_texts:
            # LLM이 점수도 함께 반환한 경우, 그 점수를 사용 (텍스트와 점수 일치)
            if 'scores' in fortune_texts:
                llm_scores = fortune_texts['scores']
                fortune_scores = {
                    'total': llm_scores.get('total', fortune_scores['total']),
                    'money': llm_scores.get('money', fortune_scores['money']),
                    'love': llm_scores.get('love', fortune_scores['love']),
                    'study': llm_scores.get('study', fortune_scores['study']),
                    'work': llm_scores.get('work', fortune_scores['work']),
                    'health': llm_scores.get('health', fortune_scores['health'])
                }
                print(f"[DEBUG] LLM 점수 사용: {fortune_scores}")

                # LLM 점수 기반으로 lucky_item 재계산 (낮은 운세 2개가 바뀔 수 있음)
                lucky_item = self._determine_lucky_item(
                    zodiac_sign, today, user_id, session_key, lucky_colors,
                    fortune_score=fortune_scores['total'],
                    fortune_scores=fortune_scores
                )

            # LLM lucky_item 설명 사용 안함 - 하드코딩된 설명 사용
            # LLM이 아이템 이름을 제대로 반영하지 않아서 비활성화
            pass
        else:
            print("[DEBUG] LLM 생성 실패, 기존 로직 사용")
            fortune_texts = self._generate_fortune_texts(fortune_scores, zodiac_sign, chinese_zodiac)
        
        return {
            'fortune_score': fortune_scores['total'],
            'fortune_scores': fortune_scores,
            'fortune_texts': fortune_texts,
            'saju_data': saju_data,
            'zodiac_sign': zodiac_sign,
            'chinese_zodiac': chinese_zodiac,
            'lucky_color': lucky_colors[0] if lucky_colors else '파란색',
            'lucky_colors': lucky_colors,
            'lotto_numbers': lotto_numbers,  # 로또 번호 추가
            'lucky_item': lucky_item,
            'calculation_date': today.isoformat(),
            'birth_date': birth_date.isoformat(),  # 미성년자 체크용
            'gender': gender,  # 로또 재생성용
            'user_id': user_id,  # 로그인 사용자 식별용
            'session_key': session_key,  # 비로그인 사용자 식별용
            'mbti': mbti  # 결과에 MBTI 포함
        }

    def _generate_fortune_text_with_llm(
        self,
        birth_date: date,
        gender: str,
        saju: Dict,
        zodiac: str,
        chinese_zodiac: str,
        scores: Dict,
        mbti: Optional[str] = None,
        lucky_item_name: Optional[str] = None,
        zodiac_item_name: Optional[str] = None
    ) -> Optional[Dict]:
        """GMS API (Claude/GPT) 또는 Gemini를 사용한 운세 텍스트 생성"""
        import time

        # 캐시 키 생성
        cache_key = f"fortune_text_{birth_date}_{gender}_{zodiac}_{chinese_zodiac}_{mbti}_{lucky_item_name}_{date.today()}"
        cached_result = cache.get(cache_key)

        if cached_result:
            print("[DEBUG] 캐시된 운세 텍스트 사용")
            return cached_result

        # GMS API 먼저 시도 (Claude 사용)
        gms_api_key = getattr(settings, 'GMS_API_KEY', '')
        gms_api_base = getattr(settings, 'GMS_API_BASE_URL', '')

        # Gemini API (백업)
        gemini_api_key = settings.GEMINI_API_KEY

        if not gms_api_key and not gemini_api_key:
            print("[ERROR] API 키가 설정되지 않음 (GMS_API_KEY 또는 GEMINI_API_KEY)")
            return None

        max_retries = 1
        retry_delay = 2  # 재시도 간 딜레이 (초)

        mbti_info = f"- MBTI: {mbti}" if mbti else "- MBTI: 정보 없음"
        lucky_item_info = f"- 운세 기반 행운 아이템: {lucky_item_name}" if lucky_item_name else ""
        zodiac_item_info = f"- 별자리 행운 아이템: {zodiac_item_name}" if zodiac_item_name else ""

        prompt = f"""
당신은 전문 운세 상담가입니다. 아래 사용자의 정보를 바탕으로 '네이버 운세' 스타일의 오늘의 운세를 작성하고, 각 운세의 점수를 매겨주세요.

[사용자 정보]
- 생년월일: {birth_date}
- 성별: {'남성' if gender == 'M' else '여성'}
- 별자리: {zodiac}
- 띠: {chinese_zodiac}
{mbti_info}
{lucky_item_info}
- 사주: {saju['year']}년 {saju['month']}월 {saju['day']}일 {saju['hour']}시 (간지)
- 오늘 날짜: {date.today()}

[작성 가이드]
1. **말투**: "~합니다", "~입니다" 체의 정중하고 부드러운 문체 (네이버 운세 스타일)
2. **길이 (매우 중요)**:
   - 각 항목당 **정확히 5문장**으로 작성해주세요.
   - 각 문장은 마침표(.)로 끝나야 합니다.
   - 3문장 이하로 작성하면 안 됩니다! 반드시 5문장을 채워주세요.
3. **점수 매기기 (중요)**:
   - 각 운세의 내용을 먼저 작성한 후, 그 내용에 맞는 점수를 50~100점 사이에서 매겨주세요.
   - 점수와 텍스트의 톤이 일치해야 합니다:
     * 90-100점: 매우 좋은 운세, 적극적으로 행동 권장
     * 75-89점: 좋은 운세, 긍정적인 기운
     * 60-74점: 보통 운세, 신중함 권장, 약간의 주의 필요
     * 50-59점: 다소 어려운 운세, 조심스러운 접근 권장
   - **운세 텍스트가 좋으면 점수도 높게, 주의가 필요한 내용이면 점수도 낮게** 매겨주세요.
4. **점수 언급 금지**: 텍스트 내에서 "90점", "85점" 등 숫자를 직접 언급하지 마세요.
5. **MBTI 반영 방식**:
   - "MBTI가 ~라서" 같은 말은 하지 마세요.
   - 사용자의 MBTI 성향에 맞는 조언을 자연스럽게 녹여내세요.
6. **행운의 아이템 설명 (중요)**:
   - 운세 기반 아이템 '{lucky_item_name}' 설명: 2문장 (60~80자)
     * 반드시 '{lucky_item_name}'이라는 단어를 설명에 포함해주세요!
     * 예: "{lucky_item_name}은(는) 오늘 당신에게 좋은 기운을 전해줍니다. 특히 대인관계에서 긍정적인 에너지를 발산합니다."
   - 별자리({zodiac}) 아이템 '{zodiac_item_name}' 설명: 2문장 (60~80자)
     * 반드시 '{zodiac_item_name}'이라는 단어를 설명에 포함해주세요!
     * 예: "{zodiac_item_name}은(는) {zodiac}인 당신에게 특별한 행운을 가져다줍니다. 오늘 하루 긍정적인 변화가 찾아올 것입니다."
   - **두 설명의 길이를 비슷하게 맞춰주세요 (차이 10자 이내)**
7. **총운 점수**: 재물운, 애정운, 학업운, 직장운, 건강운 점수의 평균을 반올림하여 총운 점수로 사용해주세요.

[출력 형식]
반드시 아래 JSON 형식으로만 출력하세요 (마크다운 코드 블록 없이 순수 JSON만):
{{{{
    "total": "총운 내용...",
    "money": "재물운 내용...",
    "love": "애정운 내용...",
    "study": "학업운 내용...",
    "work": "직장운 내용...",
    "health": "건강운 내용...",
    "scores": {{{{
        "total": 총운점수,
        "money": 재물운점수,
        "love": 애정운점수,
        "study": 학업운점수,
        "work": 직장운점수,
        "health": 건강운점수
    }}}},
    "lucky_item": {{{{
        "description": "{lucky_item_name}은(는)... (2문장, 60~80자, 아이템 이름 포함 필수)",
        "zodiac_description": "{zodiac_item_name}은(는)... (2문장, 60~80자, 아이템 이름 포함 필수)"
    }}}}
}}}}
"""

        # 1. GMS API (GPT-5-nano) 먼저 시도 - 1크레딧으로 효율적
        if gms_api_key:
            for attempt in range(max_retries + 1):
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=gms_api_key, base_url=gms_api_base)

                    print(f"[DEBUG] GMS GPT-5-nano 운세 생성 요청 (시도: {attempt + 1}/{max_retries + 1})...")
                    response = client.chat.completions.create(
                        model="gpt-5-nano",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=4000
                    )

                    text = response.choices[0].message.content.strip()
                    if text.startswith('```json'):
                        text = text[7:]
                    if text.startswith('```'):
                        text = text[3:]
                    if text.endswith('```'):
                        text = text[:-3]

                    result = json.loads(text.strip())
                    print("[DEBUG] GMS GPT-5-nano 운세 생성 성공!")

                    # 결과 캐싱 (24시간)
                    cache.set(cache_key, result, 60 * 60 * 24)
                    return result

                except Exception as e:
                    print(f"[ERROR] GMS GPT-5-nano 운세 생성 오류 (시도: {attempt + 1}): {e}")
                    if attempt < max_retries:
                        time.sleep(retry_delay)
                    continue

        # 2. Gemini API 백업 시도
        if gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')

                print("[DEBUG] Gemini 운세 생성 요청 (백업)...")
                response = model.generate_content(prompt)

                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:]
                if text.startswith('```'):
                    text = text[3:]
                if text.endswith('```'):
                    text = text[:-3]

                result = json.loads(text.strip())
                print("[DEBUG] Gemini 운세 생성 성공!")

                cache.set(cache_key, result, 60 * 60 * 24)
                return result

            except Exception as e:
                print(f"[ERROR] Gemini 운세 생성 오류: {e}")

        # 모든 API 실패
        print("[ERROR] 모든 LLM API 시도 실패, 동적 텍스트 생성으로 대체")
        return None
    
    def _calculate_all_fortunes(self, birth_date: date, today: date, saju_data: Dict = None) -> Dict:
        """각 운별 점수 계산 (사주 오행 기반, 최소 50점)"""
        base = random.randint(55, 90)  # 55~90점 사이 (기본, 50점대도 가능)

        # 사주 오행 데이터가 있으면 반영
        ohaeng_bonus = {'money': 0, 'love': 0, 'study': 0, 'work': 0}

        if saju_data and 'ohaeng_scores' in saju_data:
            ohaeng = saju_data['ohaeng_scores']
            # 오행 점수: 목(木), 화(火), 토(土), 금(金), 수(水)
            # 목 = 18, 화 = 12, 토 = 6, 금 = 16, 수 = 12 같은 형태

            # 오행별 운세 영향 매핑
            # 금(金) -> 재물운 (금전, 재물)
            # 화(火) -> 애정운 (열정, 사랑)
            # 수(水) -> 학업운 (지혜, 유연함)
            # 목(木) -> 직장운 (성장, 발전)
            # 토(土) -> 전체 안정 (균형, 중심)

            total_ohaeng = sum(ohaeng.values()) if ohaeng else 1
            avg_ohaeng = total_ohaeng / 5 if total_ohaeng > 0 else 10

            # 각 오행이 평균보다 높으면 보너스, 낮으면 페널티
            금 = ohaeng.get('금', 0)
            화 = ohaeng.get('화', 0)
            수 = ohaeng.get('수', 0)
            목 = ohaeng.get('목', 0)
            토 = ohaeng.get('토', 0)

            # 보너스 계산 (-10 ~ +10 범위)
            ohaeng_bonus['money'] = int((금 - avg_ohaeng) / avg_ohaeng * 10) if avg_ohaeng > 0 else 0
            ohaeng_bonus['love'] = int((화 - avg_ohaeng) / avg_ohaeng * 10) if avg_ohaeng > 0 else 0
            ohaeng_bonus['study'] = int((수 - avg_ohaeng) / avg_ohaeng * 10) if avg_ohaeng > 0 else 0
            ohaeng_bonus['work'] = int((목 - avg_ohaeng) / avg_ohaeng * 10) if avg_ohaeng > 0 else 0

            # 토(土)가 강하면 전체 안정 보너스
            if 토 > avg_ohaeng:
                stability_bonus = int((토 - avg_ohaeng) / avg_ohaeng * 5)
                ohaeng_bonus['money'] += stability_bonus
                ohaeng_bonus['love'] += stability_bonus
                ohaeng_bonus['study'] += stability_bonus
                ohaeng_bonus['work'] += stability_bonus

            # 일주 강약(ilju_strength)도 반영
            if saju_data.get('ilju_strength'):
                strength = saju_data['ilju_strength']
                if strength == '강':
                    base += 5  # 일주가 강하면 기본 운세 상승
                elif strength == '약':
                    base -= 3  # 일주가 약하면 기본 운세 소폭 하락

        # 오행 보너스 적용 (범위 제한: -15 ~ +15)
        ohaeng_bonus = {k: max(-15, min(15, v)) for k, v in ohaeng_bonus.items()}

        money = max(50, min(100, base + random.randint(-10, 15) + ohaeng_bonus['money']))
        love = max(50, min(100, base + random.randint(-15, 20) + ohaeng_bonus['love']))
        study = max(50, min(100, base + random.randint(-10, 10) + ohaeng_bonus['study']))
        work = max(50, min(100, base + random.randint(-10, 15) + ohaeng_bonus['work']))
        health = max(50, min(100, base + random.randint(-10, 10)))

        # 총운은 5개 운세의 평균
        total = round((money + love + study + work + health) / 5)

        return {
            'total': total,
            'money': money,
            'love': love,
            'study': study,
            'work': work,
            'health': health,
        }
    
    def _generate_fortune_texts(self, scores: Dict, zodiac_sign: str, chinese_zodiac: str) -> Dict:
        """LLM 실패 시 동적 운세 텍스트 생성 - 날짜/점수 기반 변형"""
        today = date.today()
        day_seed = today.toordinal() + hash(zodiac_sign) % 100  # 날짜+별자리 기반 시드
        random.seed(day_seed)

        # 시간대 변형 (매일 다르게)
        morning_hours = random.choice(["오전 9시", "오전 10시", "오전 11시", "아침 일찍"])
        afternoon_hours = random.choice(["오후 2시", "오후 3시", "오후 4시", "점심 이후"])
        evening_hours = random.choice(["저녁 6시", "저녁 7시", "저녁 8시", "저녁 무렵"])

        # 조언 키워드 변형
        action_words_positive = random.choice(["적극적으로", "자신감 있게", "주도적으로", "과감하게"])
        action_words_neutral = random.choice(["차분하게", "꾸준히", "성실하게", "묵묵히"])
        action_words_negative = random.choice(["신중하게", "조심스럽게", "천천히", "여유롭게"])

        # 장소 변형
        places = random.choice(["카페", "공원", "도서관", "익숙한 장소"])

        texts = {}

        # 종합운
        total_score = scores['total']
        total_templates_high = [
            f"오늘은 전반적으로 운기가 상승하는 날입니다. {morning_hours}부터 긍정적인 에너지가 느껴지며, 평소 미뤄둔 일들을 처리하기 좋습니다. 주변 사람들과의 관계에서도 좋은 일이 생길 가능성이 높으니, {action_words_positive} 행동해 보세요. {afternoon_hours}에는 예상치 못한 기쁜 소식을 들을 수도 있습니다. 오늘의 좋은 기운을 최대한 활용하여 중요한 일을 추진해 보세요.",
            f"모든 일이 순조롭게 풀리는 길일입니다. 당신의 노력이 빛을 발하는 시기이며, {action_words_positive} 도전하면 좋은 성과를 거둘 수 있습니다. {morning_hours}에 시작한 일은 특히 좋은 결과로 이어질 것입니다. 사람들과의 소통에서도 원활함이 느껴지며, 새로운 기회가 찾아올 수 있습니다. 자신을 믿고 한 걸음 더 나아가 보세요.",
            f"행운이 가득한 하루가 예상됩니다. {afternoon_hours} 무렵 좋은 소식이나 기회가 찾아올 수 있으니 열린 마음으로 받아들이세요. 오늘은 새로운 시도나 도전에도 운이 따르는 날이니, 망설이던 일이 있다면 실행에 옮겨보세요. 주변의 도움도 기대할 수 있으며, 협력하면 더 큰 성과를 얻을 수 있습니다.",
        ]
        total_templates_mid = [
            f"안정적인 기운이 감도는 하루입니다. 큰 변화보다는 {action_words_neutral} 일상을 보내는 것이 좋으며, 급한 결정은 피하는 것이 현명합니다. {morning_hours}에는 가벼운 운동이나 산책으로 하루를 시작하면 좋겠습니다. 오후에는 밀린 업무나 집안일을 정리하기에 적합한 시간입니다. 소소한 일상에서 행복을 찾아보세요.",
            f"무난하게 흘러가는 평화로운 날입니다. 특별히 좋거나 나쁜 일은 없겠지만, {action_words_neutral} 자신의 할 일에 집중하면 뿌듯한 하루를 보낼 수 있습니다. {places}에서 잠시 여유를 갖는 것도 좋겠습니다. 가까운 사람들과 소통하며 마음의 안정을 찾아보세요.",
            f"평온한 기운 속에서 자신을 돌아보기 좋은 날입니다. {action_words_neutral} 진행하던 일들을 마무리하고, 새로운 계획을 세워보세요. {evening_hours}에는 휴식을 취하며 재충전의 시간을 가지면 좋겠습니다. 작은 것에 감사하는 마음이 더 큰 행복을 가져다줄 것입니다.",
        ]
        total_templates_low = [
            f"오늘은 {action_words_negative} 움직이는 것이 좋겠습니다. 무리한 계획이나 새로운 시도는 피하고, 기존에 하던 일에 집중하세요. 컨디션이 평소보다 떨어질 수 있으니 충분한 휴식을 취하는 것이 중요합니다. {evening_hours}에는 일찍 귀가하여 편안한 시간을 보내세요. 내일은 더 나은 기운이 찾아올 것입니다.",
            f"조금은 조심스러운 하루가 될 수 있습니다. 중요한 결정이나 약속은 가능하면 연기하고, {action_words_negative} 하루를 보내세요. 사소한 일에도 신경이 쓰일 수 있으니, 마음을 편하게 먹는 것이 중요합니다. 무리하지 말고 자신의 페이스를 유지하면 무난히 넘길 수 있습니다.",
            f"재충전이 필요한 시기입니다. 오늘은 {action_words_negative} 에너지를 아끼고, 불필요한 외출이나 약속은 줄이세요. {places}에서 혼자만의 시간을 가지며 마음을 정리하는 것이 도움이 됩니다. 오늘의 휴식이 내일의 활력이 될 것입니다.",
        ]

        if total_score >= 80:
            texts['total'] = random.choice(total_templates_high)
        elif total_score >= 60:
            texts['total'] = random.choice(total_templates_mid)
        else:
            texts['total'] = random.choice(total_templates_low)

        # 재물운
        money_score = scores['money']
        money_high = [
            f"재물운이 좋은 날입니다. 예상치 못한 수입이나 좋은 거래가 성사될 가능성이 있습니다. {afternoon_hours}에 금전적으로 좋은 소식을 들을 수 있으며, 소소한 투자도 괜찮은 결과를 가져올 수 있습니다. 다만 과욕은 금물이니 적당한 선에서 만족하세요. 오늘 들어온 재물은 일부 저축하는 것이 좋겠습니다.",
            f"금전운이 상승하는 시기입니다. 새로운 수입원이 생기거나, 미수금이 회수될 가능성이 있습니다. 재테크에 관심이 있다면 정보를 수집하기 좋은 때입니다. {morning_hours}에 재정 관련 결정을 내리면 좋은 결과가 있을 것입니다. 너무 큰 욕심보다는 안정적인 성장을 목표로 하세요.",
        ]
        money_mid = [
            f"재물운이 안정적인 날입니다. 큰 수입은 없지만 지출도 적을 것입니다. 계획적인 소비를 하면 무난한 하루를 보낼 수 있으며, 미래를 위한 저축을 시작하기 좋은 때입니다. 불필요한 충동구매는 자제하고, 꼭 필요한 것만 구입하세요.",
            f"금전적으로 무난한 흐름입니다. 현재 상태를 유지하는 것이 좋으며, 큰 투자나 지출은 피하는 것이 현명합니다. 가계부를 정리하거나 재정 상태를 점검해보는 시간을 가지면 좋겠습니다.",
        ]
        money_low = [
            f"재물운이 다소 저조한 날입니다. 충동구매나 불필요한 지출을 자제하고, 계획에 없던 소비는 최대한 피하세요. 투자나 도박성 거래는 절대 피해야 하며, 금전 대출이나 보증도 서지 않는 것이 좋습니다. 어려운 시기는 곧 지나갈 것입니다.",
            f"지갑을 단단히 여미는 것이 좋은 날입니다. 예상치 못한 지출이 발생할 수 있으니 여유 자금을 확보해두세요. 오늘은 돈을 버는 것보다 지키는 것에 집중하세요.",
        ]

        if money_score >= 80:
            texts['money'] = random.choice(money_high)
        elif money_score >= 60:
            texts['money'] = random.choice(money_mid)
        else:
            texts['money'] = random.choice(money_low)

        # 연애운
        love_score = scores['love']
        love_high = [
            f"연애운이 빛나는 날입니다. 싱글이라면 매력적인 이성을 만날 기회가 있으며, {evening_hours}에 특별한 인연이 찾아올 수 있습니다. 연인이 있다면 깊은 대화와 함께 관계가 더욱 돈독해질 것입니다. 상대방에 대한 작은 배려가 큰 감동을 줄 수 있는 날입니다.",
            f"사랑의 기운이 충만한 하루입니다. 평소 호감이 있던 사람에게 다가가기 좋은 시기이며, 고백을 계획 중이라면 오늘이 적기일 수 있습니다. 연인과 함께라면 {places}에서 로맨틱한 시간을 보내보세요.",
        ]
        love_mid = [
            f"연애운이 평온한 날입니다. 큰 변화보다는 일상의 소소한 애정 표현이 중요합니다. 연인과 함께 조용한 시간을 보내거나, 진솔한 대화를 나눠보세요. 싱글이라면 자연스러운 만남을 기다리는 것이 좋습니다.",
            f"사랑에 있어 차분한 흐름입니다. 급하게 관계를 발전시키기보다 서로를 이해하는 시간을 가지세요. 주변 사람들과의 교류를 통해 새로운 인연을 만날 가능성도 있습니다.",
        ]
        love_low = [
            f"연애운이 다소 침체된 날입니다. 연인과의 사소한 오해나 다툼에 주의하고, 감정적인 대화는 피하는 것이 좋습니다. 싱글이라면 오늘은 자기 자신에게 집중하는 시간을 가져보세요. 자기 계발에 투자하면 나중에 더 좋은 인연이 찾아올 것입니다.",
            f"관계에서 신중함이 필요한 날입니다. 상대방의 말에 예민하게 반응하지 말고, 한 발짝 물러서서 상황을 바라보세요. 잠시 거리를 두는 것이 관계에 도움이 될 수 있습니다.",
        ]

        if love_score >= 80:
            texts['love'] = random.choice(love_high)
        elif love_score >= 60:
            texts['love'] = random.choice(love_mid)
        else:
            texts['love'] = random.choice(love_low)

        # 학업운
        study_score = scores['study']
        study_high = [
            f"학업운이 최상인 날입니다. 집중력이 크게 향상되어 {morning_hours}부터 {afternoon_hours}까지가 황금 시간대입니다. 어려웠던 개념도 쉽게 이해할 수 있으며, 새로운 공부를 시작하기에도 좋습니다. {places}에서 공부하면 효율이 더욱 높아질 것입니다.",
            f"배움의 운이 트이는 날입니다. 시험을 앞두고 있다면 오늘 집중적으로 공부하세요. 기억력과 이해력이 평소보다 좋아 공부한 내용이 오래 남을 것입니다.",
        ]
        study_mid = [
            f"학업에 있어 안정적인 흐름입니다. 새로운 것보다는 복습에 집중하면 좋은 성과를 얻을 수 있습니다. 동료나 스터디 그룹과의 토론도 도움이 됩니다. {action_words_neutral} 공부하는 것이 효과적입니다.",
            f"꾸준히 노력하면 결실을 맺는 날입니다. 무리하지 않는 선에서 학습 계획을 세우고 실천해보세요. 적절한 휴식과 함께 효율적으로 공부하는 것이 중요합니다.",
        ]
        study_low = [
            f"학업에 집중하기 어려운 날일 수 있습니다. 무리하지 말고 가벼운 복습 위주로 하루를 마무리하세요. 피곤함이 느껴진다면 충분한 휴식을 취한 후 다시 시작하는 것이 낫습니다. {action_words_negative} 접근하세요.",
            f"컨디션 조절이 필요한 날입니다. 오래 앉아 공부하기보다 짧게 집중하고 자주 쉬는 방식이 효과적입니다. 어려운 내용은 내일로 미루고 오늘은 쉬운 것부터 해보세요.",
        ]

        if study_score >= 80:
            texts['study'] = random.choice(study_high)
        elif study_score >= 60:
            texts['study'] = random.choice(study_mid)
        else:
            texts['study'] = random.choice(study_low)

        # 직장운
        work_score = scores['work']
        work_high = [
            f"직장운이 상승하는 날입니다. 당신의 능력과 노력이 인정받을 가능성이 높으며, {afternoon_hours}에 좋은 소식을 들을 수 있습니다. 중요한 미팅이나 발표가 있다면 자신감을 가지고 임하세요. 동료들과의 협업도 원활하게 이루어질 것입니다.",
            f"커리어에 있어 기회의 날입니다. 새로운 프로젝트나 역할을 맡게 될 수 있으며, {action_words_positive} 임하면 좋은 결과를 얻을 수 있습니다. 상사나 고객에게 좋은 인상을 줄 수 있는 기회가 있습니다.",
        ]
        work_mid = [
            f"업무가 무난하게 흘러가는 날입니다. 큰 성과는 없더라도 맡은 일을 {action_words_neutral} 처리하면 됩니다. 미뤄둔 업무를 정리하기 좋은 때이며, 동료들과 원활한 소통이 가능합니다.",
            f"안정적인 업무 흐름입니다. 새로운 도전보다는 현재 진행 중인 일에 집중하세요. 성실함이 장기적으로 좋은 결과를 가져올 것입니다.",
        ]
        work_low = [
            f"직장에서 {action_words_negative} 행동하는 것이 좋겠습니다. 중요한 결정이나 새로운 제안은 미루고, 평소 하던 일에만 집중하세요. 동료나 상사와의 의견 충돌에 주의하고, 감정적인 대응은 피하세요.",
            f"업무 스트레스가 있을 수 있는 날입니다. 완벽함을 추구하기보다 무난하게 하루를 마무리하는 것을 목표로 하세요. 실수를 줄이기 위해 중요한 일은 이중 체크하세요.",
        ]

        if work_score >= 80:
            texts['work'] = random.choice(work_high)
        elif work_score >= 60:
            texts['work'] = random.choice(work_mid)
        else:
            texts['work'] = random.choice(work_low)

        # 건강운
        health_score = scores.get('health', 70)
        health_high = [
            f"건강운이 좋은 날입니다. 몸과 마음 모두 활력이 넘치며, 새로운 운동을 시작하기에 좋은 시기입니다. {morning_hours}에 가벼운 운동으로 하루를 시작하면 상쾌한 기분이 종일 유지될 것입니다. 충분한 수분 섭취도 잊지 마세요.",
            f"에너지가 넘치는 하루입니다. 평소 하고 싶었던 야외 활동이나 운동을 즐기기 좋습니다. 면역력도 좋은 상태이니 건강 검진이나 운동 계획을 실행해보세요.",
        ]
        health_mid = [
            f"건강운이 안정적인 날입니다. 무리하지 않는 선에서 규칙적인 생활을 유지하면 좋겠습니다. 가벼운 스트레칭이나 산책이 도움이 되며, 충분한 수면도 중요합니다.",
            f"몸 상태가 평온한 날입니다. 자극적인 음식은 피하고, 균형 잡힌 식사를 하세요. 틈틈이 휴식을 취하며 컨디션을 유지하는 것이 중요합니다.",
        ]
        health_low = [
            f"건강 관리에 신경 써야 하는 날입니다. 무리한 활동은 피하고, {evening_hours}에는 일찍 휴식을 취하세요. 소화가 안 될 수 있으니 가벼운 음식 위주로 드시고, 충분한 수면이 필요합니다.",
            f"컨디션이 떨어질 수 있는 날입니다. 격한 운동보다는 가벼운 스트레칭 정도가 적합하며, 몸의 신호에 귀 기울이세요. 충분히 쉬면 내일은 회복될 것입니다.",
        ]

        if health_score >= 80:
            texts['health'] = random.choice(health_high)
        elif health_score >= 60:
            texts['health'] = random.choice(health_mid)
        else:
            texts['health'] = random.choice(health_low)

        # 랜덤 시드 리셋 (다른 곳에 영향 안 주도록)
        random.seed()

        return texts
    
    def _determine_lucky_colors(
        self,
        zodiac_sign: str,
        chinese_zodiac: str,
        today: date,
        fortune_scores: Dict = None
    ) -> List[str]:
        """행운의 색상들 결정 (별자리 + 띠 + 날짜 + 운세점수 기반)"""
        import hashlib

        # 시드 생성: 별자리 + 띠 + 날짜 조합으로 매일 다른 결과
        seed_string = f"{zodiac_sign}_{chinese_zodiac}_{today.isoformat()}"
        seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)

        # 별자리 색상 풀
        star_colors = self.STAR_SIGN_COLORS.get(zodiac_sign, self.ALL_COLORS[:5])

        # 띠 색상 풀
        zodiac_colors = self.CHINESE_ZODIAC_COLORS.get(chinese_zodiac, [])

        # 후보 색상 풀 구성 (별자리 + 띠 색상 합치기)
        candidate_colors = list(star_colors) + list(zodiac_colors)

        # 운세 점수가 있으면 점수에 따라 색상 가중치 조정
        if fortune_scores:
            total_score = fortune_scores.get('total', 50)

            # 운세가 좋으면 밝은 색상 추가
            if total_score >= 80:
                candidate_colors.extend(['금색', '노란색', '흰색'])
            elif total_score >= 60:
                candidate_colors.extend(['하늘색', '분홍색'])
            elif total_score < 40:
                # 운세가 낮으면 안정적인 색상 추가
                candidate_colors.extend(['남색', '회색', '베이지색'])

        # 중복 제거
        candidate_colors = list(dict.fromkeys(candidate_colors))

        # 날짜 기반 시드로 3개 선택 (같은 날짜면 같은 결과)
        selected_colors = []
        for i in range(3):
            if not candidate_colors:
                break
            # 시드 + 인덱스로 선택
            idx = (seed_hash + i * 7) % len(candidate_colors)
            selected_colors.append(candidate_colors[idx])
            candidate_colors.pop(idx)  # 중복 선택 방지

        # 3개 미만이면 전체 풀에서 보충
        if len(selected_colors) < 3:
            remaining = [c for c in self.ALL_COLORS if c not in selected_colors]
            for i in range(3 - len(selected_colors)):
                if remaining:
                    idx = (seed_hash + i * 13) % len(remaining)
                    selected_colors.append(remaining[idx])
                    remaining.pop(idx)

        return selected_colors if selected_colors else ['파란색', '초록색', '노란색']

    def _generate_lucky_lotto_numbers(
        self,
        birth_date: date,
        today: date,
        fortune_scores: Dict = None,
        gender: str = None,
        user_id: int = None,
        session_key: str = None
    ) -> List[int]:
        """개인별 행운의 로또 번호 생성 (user_id 또는 session_key 기반)"""
        import hashlib

        # 성별 숫자 변환
        gender_num = 1 if gender == 'M' else 2 if gender == 'F' else 0

        # 사용자 식별자 결정: user_id 우선, 없으면 session_key
        if user_id:
            user_identifier = f"user_{user_id}"
        elif session_key:
            user_identifier = f"session_{session_key}"
        else:
            import uuid
            user_identifier = f"random_{uuid.uuid4()}"

        # 시드 생성: 사용자식별자 + 오늘날짜 + 생년월일 + 성별
        # 로그인 사용자는 브라우저 바뀌어도 같은 번호, 비로그인은 세션 기반
        birth_num = birth_date.year * 10000 + birth_date.month * 100 + birth_date.day
        base_seed = f"lotto_{user_identifier}_{today.isoformat()}_{birth_num}_{gender_num}"

        # 순수 해시 기반으로 6개 고유 번호 선택 (random 모듈 미사용)
        selected = []
        attempt = 0
        while len(selected) < 6 and attempt < 100:
            # 각 번호마다 다른 해시 생성
            seed_string = f"{base_seed}_num{attempt}"
            hash_value = int(hashlib.sha256(seed_string.encode()).hexdigest(), 16)
            num = (hash_value % 45) + 1  # 1-45 범위

            if num not in selected:
                selected.append(num)
            attempt += 1

        return sorted(selected)

    def _determine_lucky_item(self, zodiac_sign: str, today: date, user_id: int = None, session_key: str = None, lucky_colors: List[str] = None, fortune_score: int = 70, fortune_scores: Dict = None) -> Dict:
        """행운의 아이템 결정 - 점수대별 6개 아이템, 낮은 운 2개 조합(4C2=6)으로 선택"""
        import hashlib

        # 낮은 운 2개 조합별 인덱스 매핑 (4C2 = 6가지)
        # 0: 재물+애정, 1: 재물+학업, 2: 재물+직장, 3: 애정+학업, 4: 애정+직장, 5: 학업+직장
        combo_to_index = {
            ('love', 'money'): 0,
            ('money', 'study'): 1,
            ('money', 'work'): 2,
            ('love', 'study'): 3,
            ('love', 'work'): 4,
            ('study', 'work'): 5,
        }

        # 고득점(80+): 적극적/활동적 아이템 6개
        high_score_items = [
            ('미니 향수', '🌸', '재물운', '애정운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 미니 향수입니다. 은은한 향기는 주변 사람들에게 호감을 주어 소중한 인연을 맺게 해주고, 좋은 기회도 자연스럽게 찾아오게 합니다. 자신감 있는 하루를 보내며 적극적으로 행동해보세요.'),
            ('명함지갑', '💼', '재물운', '학업운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 명함지갑입니다. 체계적으로 정리하는 습관은 업무와 학습 효율을 높여주고, 재정 관리 능력도 함께 향상시켜 줍니다. 오늘 하루 계획을 세우고 차근차근 실천해보세요.'),
            ('손목시계', '⌚', '재물운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 손목시계입니다. 시간을 소중히 여기는 당신에게 손목시계는 성실함과 신뢰를 상징합니다. 정확한 시간 관리가 좋은 성과와 보상으로 이어질 것입니다.'),
            ('미니 키링', '🔑', '애정운', '학업운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 미니 키링입니다. 새로운 문을 여는 열쇠처럼, 키링은 좋은 인연과 새로운 배움의 기회를 열어줍니다. 열린 마음으로 하루를 시작해보세요.'),
            ('스카프', '🧣', '애정운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 스카프입니다. 우아한 스카프는 당신의 매력을 한층 돋보이게 하여 좋은 첫인상을 만들어줍니다. 대인관계가 원만해지고 좋은 일이 생길 것입니다.'),
            ('볼펜', '🖊️', '학업운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 볼펜입니다. 기록하는 습관은 흩어진 생각을 정리하고 좋은 아이디어를 떠올리게 합니다. 오늘 떠오르는 영감을 놓치지 말고 기록해보세요.'),
        ]

        # 중간점수(60-79): 안정적/균형 아이템 6개
        mid_score_items = [
            ('손수건', '🤍', '재물운', '애정운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 손수건입니다. 정성이 담긴 손수건은 따뜻한 마음을 전해 소중한 인연을 더욱 깊게 만들어줍니다. 작은 배려가 큰 행운으로 돌아올 것입니다.'),
            ('다이어리', '📔', '재물운', '학업운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 다이어리입니다. 꼼꼼하고 계획적인 당신에게 다이어리는 그 능력을 더욱 발휘할 수 있도록 도와줍니다. 오늘 할 일 목록을 작성하고 계획대로 실천한다면 성취감을 얻을 수 있을 것입니다.'),
            ('카드지갑', '💳', '재물운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 카드지갑입니다. 깔끔하게 정리된 카드지갑은 체계적인 금전 관리와 신뢰감 있는 이미지를 만들어줍니다. 차분하게 하루를 보내세요.'),
            ('북마크', '📚', '애정운', '학업운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 북마크입니다. 책갈피처럼 소중한 순간을 기억하며, 지식과 사랑이 함께 자라납니다. 오늘 읽은 책의 한 구절이 영감을 줄 것입니다.'),
            ('손거울', '🪞', '애정운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 손거울입니다. 자신을 돌아보는 여유가 내면의 자신감을 높여주고 대인관계를 개선해줍니다. 잠시 멈춰서 자신을 되돌아보는 시간을 가져보세요.'),
            ('텀블러', '🥤', '학업운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 텀블러입니다. 건강한 수분 섭취 습관은 맑은 정신과 높은 집중력을 유지하게 해줍니다. 오늘 하루 충분히 물을 마시며 활력을 채워보세요.'),
        ]

        # 저득점(60 미만): 보호/안정 아이템 6개
        low_score_items = [
            ('동전 키링', '🪙', '재물운', '애정운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 동전 키링입니다. 작은 동전 하나가 금전운을 지켜주고 소중한 인연을 보호해줍니다. 무리하지 말고 안정적으로 하루를 보내세요.'),
            ('메모장', '📝', '재물운', '학업운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 메모장입니다. 떠오르는 생각을 바로 기록하면 좋은 아이디어와 절약 습관이 길러집니다. 작은 것부터 차근차근 정리해보세요.'),
            ('머플러', '🧶', '재물운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 머플러입니다. 따뜻하게 감싸주는 머플러처럼 보호의 기운이 재정 안정과 커리어 성장을 도와줍니다. 몸과 마음을 따뜻하게 유지하세요.'),
            ('헤어핀', '📎', '애정운', '학업운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 헤어핀입니다. 작은 포인트 하나가 당신의 매력을 높이고 집중력을 향상시켜줍니다. 자신을 가꾸는 작은 노력이 좋은 결과를 가져올 것입니다.'),
            ('립밤', '💋', '애정운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 립밤입니다. 자신을 가꾸는 작은 습관이 자신감을 높이고 대인관계를 개선합니다. 오늘 하루 자신에게 조금 더 신경 써보세요.'),
            ('미니 파우치', '👝', '학업운', '직장운',
             '오늘 당신에게 행운을 가져다 줄 아이템은 미니 파우치입니다. 정리된 소지품처럼 마음을 정돈하면 학습과 업무에 더 집중할 수 있습니다. 주변을 깔끔하게 정리해보세요.'),
        ]

        # 별자리별 아이템 매핑
        zodiac_items = {
            '양자리': ('팔찌', '⭕',
                    '적극적인 양자리인 당신에게 팔찌는 열정과 용기를 불어넣어줍니다. 오늘 하루 팔찌를 착용하고 자신감을 가지면 긍정적인 에너지를 발산할 수 있을 것입니다.'),
            '황소자리': ('키홀더', '🔗',
                     '안정을 추구하는 황소자리인 당신에게 키홀더는 재물운과 평화로운 마음을 선사합니다. 오늘 하루 키홀더를 가까이 두고 차분하게 보내면 좋은 일이 생길 것입니다.'),
            '쌍둥이자리': ('미니 노트', '📓',
                      '소통의 달인 쌍둥이자리인 당신에게 미니 노트는 좋은 아이디어와 인연을 가져다줍니다. 떠오르는 생각을 기록하다 보면 예상치 못한 행운을 만날 수 있을 것입니다.'),
            '게자리': ('귀걸이', '✨',
                    '감성적인 게자리인 당신에게 귀걸이는 마음의 안정과 가족의 화목을 가져다줍니다. 오늘 하루 귀걸이를 착용하면 따뜻한 에너지가 주변에 퍼져나갈 것입니다.'),
            '사자자리': ('반지', '💫',
                     '당당한 사자자리인 당신에게 반지는 리더십과 카리스마를 높여줍니다. 오늘 반지를 착용하고 자신감 있게 행동하면 주변의 인정을 받을 수 있을 것입니다.'),
            '처녀자리': ('펜케이스', '✏️',
                     '꼼꼼한 처녀자리인 당신에게 정리된 펜케이스는 집중력과 성공을 가져다줍니다. 오늘 깔끔하게 정리된 물건들 사이에서 영감을 얻을 수 있을 것입니다.'),
            '천칭자리': ('헤어밴드', '🎀',
                     '균형을 추구하는 천칭자리인 당신에게 헤어밴드는 평화와 좋은 첫인상을 선사합니다. 오늘 헤어밴드로 단정하게 꾸미면 좋은 인연을 만날 수 있을 것입니다.'),
            '전갈자리': ('목걸이', '📿',
                     '깊은 통찰력의 전갈자리인 당신에게 목걸이는 보호와 직관력을 높여줍니다. 오늘 하루 목걸이를 착용하고 자신감을 가지면 긍정적인 에너지를 발산할 수 있을 것입니다.'),
            '사수자리': ('파우치', '🧳',
                     '자유로운 사수자리인 당신에게 파우치는 행운과 새로운 모험의 기운을 줍니다. 오늘 파우치에 소중한 물건을 넣어 다니면 좋은 기회가 찾아올 것입니다.'),
            '염소자리': ('시계', '⏰',
                     '성실한 염소자리인 당신에게 시계는 인내와 노력에 대한 정확한 보상을 가져다줍니다. 오늘 시간을 잘 관리하면 원하는 목표에 한 걸음 더 가까워질 것입니다.'),
            '물병자리': ('뱃지', '🎖️',
                     '독창적인 물병자리인 당신에게 뱃지는 영감과 창의력을 불어넣어줍니다. 오늘 뱃지를 달고 자신만의 개성을 표현하면 특별한 기회가 찾아올 것입니다.'),
            '물고기자리': ('브로치', '🌙',
                      '감수성 풍부한 물고기자리인 당신에게 브로치는 직관과 내면의 평화를 가져다줍니다. 오늘 브로치를 착용하면 마음이 안정되고 좋은 영감을 받을 수 있을 것입니다.'),
        }

        # 운 종류 이름 매핑
        fortune_names = {
            'money': '재물운',
            'love': '애정운',
            'study': '학업운',
            'work': '직장운'
        }

        # 기본 운세 점수 (fortune_scores가 없을 경우)
        if not fortune_scores:
            fortune_scores = {
                'money': 70,
                'love': 70,
                'study': 70,
                'work': 70
            }

        # 4가지 운 중 가장 낮은 2개 찾기
        sub_scores = {
            'money': fortune_scores.get('money', 70),
            'love': fortune_scores.get('love', 70),
            'study': fortune_scores.get('study', 70),
            'work': fortune_scores.get('work', 70)
        }
        sorted_scores = sorted(sub_scores.items(), key=lambda x: x[1])
        lowest_two = tuple(sorted([sorted_scores[0][0], sorted_scores[1][0]]))  # 정렬해서 키로 사용

        # 낮은 운 2개 조합으로 아이템 인덱스 결정
        item_idx = combo_to_index.get(lowest_two, 0)

        # 총점 기반 아이템 풀 선택
        if fortune_score >= 80:
            item_pool = high_score_items
        elif fortune_score >= 60:
            item_pool = mid_score_items
        else:
            item_pool = low_score_items

        # 해당 인덱스의 아이템 선택
        selected_item = item_pool[item_idx]

        # 설명 생성
        lowest_fortune_name = fortune_names[sorted_scores[0][0]]
        second_fortune_name = fortune_names[sorted_scores[1][0]]

        # 운세 기반 아이템 설명 (아이템 데이터의 설명 직접 사용)
        main_description = selected_item[4]

        # 별자리 아이템 선택
        zodiac_item = zodiac_items.get(zodiac_sign, ('반지', '💫', '당신에게 반지는 전반적인 행운을 가져다줍니다. 오늘 하루 반지를 착용하고 긍정적인 마음으로 보내면 좋은 일이 생길 것입니다.'))

        # 별자리 아이템 설명 (2문장, 약 70~80자)
        zodiac_description = zodiac_item[2]

        return {
            'main': selected_item[0],
            'emoji': selected_item[1],
            'description': main_description,
            'weak_fortunes': f"{lowest_fortune_name}, {second_fortune_name}",
            'zodiac': zodiac_item[0],
            'zodiac_emoji': zodiac_item[1],
            'zodiac_description': zodiac_description
        }

   
    def _calculate_saju(self, birth_date: date, birth_time: Optional[datetime] = None) -> Dict:
        """사주 계산 (정확한 만세력 기준)"""
        try:
            result = self.saju_calc.calculate_saju(birth_date, birth_time)
            return {
                'year': result['saju']['year']['ganzi'],
                'month': result['saju']['month']['ganzi'],
                'day': result['saju']['day']['ganzi'],
                'hour': result['saju']['hour']['ganzi'],
                'year_stem': result['saju']['year']['gan'],
                'year_branch': result['saju']['year']['ji'],
                'year_hanja': result['year_hanja'],
                'month_hanja': result['month_hanja'],
                'day_hanja': result['day_hanja'],
                'hour_hanja': result['hour_hanja'],
                'ohaeng_scores': result['ohaeng_scores'],
                'day_ohaeng': result['day_ohaeng'],
                'strongest_ohaeng': result['strongest_ohaeng'],
                'ilju_strength': result['ilju_strength']
            }
        except Exception as e:
            print(f"[ERROR] 사주 계산 오류: {e}, 기존 로직 사용")
            # 폴백: 기존 간단 계산
            heavenly_stems = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
            earthly_branches = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
            
            year = birth_date.year
            year_stem = heavenly_stems[(year - 4) % 10]
            year_branch = earthly_branches[(year - 4) % 12]
            month_stem = heavenly_stems[birth_date.month % 10]
            month_branch = earthly_branches[birth_date.month % 12]
            day_stem = heavenly_stems[birth_date.day % 10]
            day_branch = earthly_branches[birth_date.day % 12]
            
            if birth_time:
                hour_stem = heavenly_stems[birth_time.hour % 10]
                hour_branch = earthly_branches[birth_time.hour % 12]
            else:
                hour_stem = heavenly_stems[0]
                hour_branch = earthly_branches[0]
            
            return {
                'year': f"{year_stem}{year_branch}",
                'month': f"{month_stem}{month_branch}",
                'day': f"{day_stem}{day_branch}",
                'hour': f"{hour_stem}{hour_branch}",
                'year_stem': year_stem,
                'year_branch': year_branch
            }
    
    def _get_zodiac_sign(self, birth_date: date) -> str:
        """별자리 계산"""
        month = birth_date.month
        day = birth_date.day
        
        signs = [
            (1, 20, '염소자리'),
            (2, 19, '물병자리'),
            (3, 21, '물고기자리'),
            (4, 20, '양자리'),
            (5, 21, '황소자리'),
            (6, 22, '쌍둥이자리'),
            (7, 23, '게자리'),
            (8, 23, '사자자리'),
            (9, 23, '처녀자리'),
            (10, 23, '천칭자리'),
            (11, 23, '전갈자리'),
            (12, 22, '사수자리'),
            (12, 31, '염소자리'),
        ]
        
        for end_month, end_day, sign in signs:
            if month < end_month or (month == end_month and day <= end_day):
                return sign
        return '염소자리'
    
    def _get_chinese_zodiac(self, birth_date: date) -> str:
        """띠 계산 (입춘 기준 - 양력용)"""
        year = birth_date.year

        # 입춘 날짜 계산 (SajuCalculator의 로직 사용)
        ipchun = self.saju_calc._get_ipchun_date(year)

        # 입춘 전이면 전년도의 띠
        if birth_date < ipchun:
            year -= 1

        zodiacs = ['원숭이', '닭', '개', '돼지', '쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양']
        return zodiacs[year % 12] + '띠'

    def _get_chinese_zodiac_lunar(self, lunar_date: date) -> str:
        """띠 계산 (음력 설날 기준 - 음력용)"""
        year = lunar_date.year

        # 음력 1월 1일 (설날) 전이면 전년도의 띠
        if lunar_date.month == 1 and lunar_date.day == 1:
            # 설날 당일은 새해의 띠
            pass
        elif lunar_date.month > 1:
            # 1월 이후는 당해년도의 띠
            pass
        # 실제로는 음력은 항상 년도만으로 판단 (음력 1/1이 설날)
        # 음력 12월생은 전년도가 아니라 해당 년도

        zodiacs = ['원숭이', '닭', '개', '돼지', '쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양']
        return zodiacs[year % 12] + '띠'
    
