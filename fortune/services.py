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
        """Gemini를 사용한 운세 텍스트 생성 (캐싱 적용)"""
        # 캐시 키 생성
        cache_key = f"fortune_text_{birth_date}_{gender}_{zodiac}_{chinese_zodiac}_{mbti}_{lucky_item_name}_{date.today()}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            print("[DEBUG] 캐시된 운세 텍스트 사용")
            return cached_result

        try:
            import google.generativeai as genai
            
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                return None
                
            genai.configure(api_key=api_key)
            
            # 모델 설정 (flash 모델 우선)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
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
2. **길이**: 각 항목당 6~8문장 (약 400자 내외) - **충분히 길고 상세하게 작성해주세요.**
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
            print("[DEBUG] Gemini 운세 생성 요청...")
            response = model.generate_content(prompt)
            
            # JSON 파싱
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            
            result = json.loads(text.strip())
            print("[DEBUG] Gemini 운세 생성 성공!")
            
            # 결과 캐싱 (24시간)
            cache.set(cache_key, result, 60 * 60 * 24)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Gemini 운세 생성 중 오류: {e}")
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
        """각 운별 상세 텍스트 생성 (250-300자)"""
        texts = {}
        
        # 종합운
        total_score = scores['total']
        if total_score >= 80:
            texts['total'] = (
                f"오늘은 {zodiac_sign}인 당신에게 정말 특별한 하루가 될 것입니다. "
                f"평소 고민하던 일들이 술술 풀리며, 주변 사람들로부터 좋은 소식을 듣게 될 가능성이 높습니다. "
                f"오전 시간대에는 중요한 결정을 내리기에 최적의 타이밍이며, 당신의 직감이 특히 예리해질 것입니다. "
                f"오후에는 새로운 인연을 만나거나 기존 관계가 더욱 돈독해질 수 있는 기회가 찾아올 것입니다. "
                f"자신감을 가지고 적극적으로 행동한다면 예상보다 훨씬 좋은 결과를 얻을 수 있을 것입니다. "
                f"특히 오늘은 {chinese_zodiac}의 기운이 강하게 작용하여 평소보다 더 많은 행운이 따를 것입니다."
            )
        elif total_score >= 60:
            texts['total'] = (
                f"{chinese_zodiac}인 당신의 오늘은 평온하고 안정적인 기운이 감돕니다. "
                f"큰 변화보다는 일상의 소소한 행복을 느낄 수 있는 날이 될 것이며, 가족이나 친구들과의 따뜻한 시간이 당신에게 위안을 줄 것입니다. "
                f"업무나 학업에서는 꾸준한 노력이 서서히 결실을 맺기 시작하는 시기입니다. "
                f"오늘 하루는 무리하지 말고 자신의 페이스를 유지하면서 차근차근 일을 진행해 나가세요. "
                f"건강 관리에도 신경을 쓰면 좋을 날이며, 가벼운 운동이나 산책이 심신의 안정에 도움이 될 것입니다."
            )
        elif total_score >= 40:
            texts['total'] = (
                f"오늘은 조금 신중하게 행동하는 것이 필요한 날입니다. "
                f"{zodiac_sign}의 기운이 다소 약해져 있어 평소보다 집중력이 떨어질 수 있습니다. "
                f"중요한 결정은 하루 이틀 미루는 것이 현명하며, 충분한 시간을 갖고 깊이 있게 고민해보세요. "
                f"대인관계에서는 오해가 생기지 않도록 말과 행동에 특별히 주의를 기울이는 것이 좋습니다. "
                f"작은 실수가 큰 문제로 이어질 수 있으니 평소보다 꼼꼼하게 일을 처리하세요. "
                f"오늘은 새로운 시도보다는 기존에 하던 일에 충실하는 것이 더 좋은 결과를 가져올 것입니다."
            )
        else:
            texts['total'] = (
                f"오늘은 충분한 휴식이 필요한 날입니다. {chinese_zodiac}의 운세가 저조한 상태이므로 무리하지 마세요. "
                f"큰 계획이나 중요한 약속은 가능한 한 다른 날로 미루는 것이 좋겠습니다. "
                f"몸과 마음이 지쳐있을 수 있으니 충분한 수면과 영양 섭취에 신경 쓰세요. "
                f"스트레스를 받을 수 있는 상황은 최대한 피하고, 혼자만의 시간을 가지며 마음을 정리해보세요. "
                f"오늘의 휴식이 내일의 활력이 될 것이니 조급해하지 마시고, 자신을 위한 재충전의 시간으로 활용하세요."
            )
        
        # 재물운
        money_score = scores['money']
        if money_score >= 80:
            texts['money'] = (
                "재물운이 크게 상승하는 매우 좋은 날입니다. 예상치 못한 수입이나 보너스, 용돈 등의 횡재수가 있을 수 있습니다. "
                "투자나 사업에 관심이 있었다면 오늘 구체적인 계획을 세워보는 것도 좋습니다. "
                "복권이나 경품 응모에도 운이 따를 수 있으니 소소한 시도를 해보세요. "
                "다만 과도한 욕심은 오히려 손실을 가져올 수 있으니 적당한 선에서 만족하는 것이 중요합니다. "
                "오늘 들어온 재물은 미래를 위해 일부는 저축하는 것이 좋겠습니다. "
                "특히 오후 3시에서 5시 사이에 금전 관련 좋은 소식을 들을 가능성이 높습니다."
            )
        elif money_score >= 60:
            texts['money'] = (
                "재물운이 안정적으로 유지되는 무난한 날입니다. 큰 수입은 없지만 예상치 못한 지출도 없을 것입니다. "
                "계획적인 소비와 저축을 실천하기에 좋은 시기이며, 가계부를 정리하거나 재정 계획을 세우기에 적합합니다. "
                "작은 절약이 큰 부를 만든다는 마음가짐으로 불필요한 지출을 줄이면 좋은 결과가 있을 것입니다. "
                "투자보다는 안정적인 저축에 집중하는 것이 유리하며, 장기적인 재테크 공부를 시작해보는 것도 좋겠습니다. "
                "동료나 친구와 금전 거래는 가능한 피하는 것이 관계를 위해서도 좋습니다. "
                "오늘은 미래의 재정 계획을 차분히 검토해보는 시간을 가져보세요."
            )
        else:
            texts['money'] = (
                "재물운이 다소 저조한 날이니 지출 관리에 특별히 신경 써야 합니다. "
                "충동구매나 불필요한 지출을 자제하고, 꼭 필요한 것만 구입하도록 하세요. "
                "투자나 도박성 게임은 절대 피해야 하며, 금전 대출이나 보증도 서지 않는 것이 좋습니다. "
                "오늘은 돈을 쓰는 것보다 버는 방법을 고민하고, 부업이나 새로운 수입원을 찾아보는 시간을 가져보세요. "
                "작은 액수라도 저축하는 습관을 기르면 앞으로의 재물운 상승에 도움이 될 것입니다. "
                "어려운 시기는 곧 지나갈 것이니 너무 걱정하지 마시고 차분히 대처하세요."
            )
        
        # 연애운
        love_score = scores['love']
        if love_score >= 80:
            texts['love'] = (
                "연애운이 최고조에 달하는 환상적인 날입니다. 싱글이라면 운명적인 만남이나 이상형에 가까운 사람을 만날 가능성이 높습니다. "
                "연인이 있다면 서로의 사랑을 더욱 깊이 확인하고, 관계가 한 단계 발전하는 계기가 될 수 있습니다. "
                "평소 고백을 망설였다면 오늘이 최적의 타이밍이니 용기를 내보세요. "
                "데이트를 계획하고 있다면 로맨틱한 분위기의 장소를 선택하면 더욱 좋은 추억을 만들 수 있을 것입니다. "
                "상대방에 대한 작은 배려와 관심 표현이 큰 감동으로 이어질 수 있는 날입니다. "
                "특히 저녁 7시에서 9시 사이가 사랑의 기운이 가장 강한 시간대입니다."
            )
        elif love_score >= 60:
            texts['love'] = (
                "연애운이 평온하게 유지되는 안정적인 날입니다. 큰 변화보다는 일상의 소소한 애정 표현이 중요한 시기입니다. "
                "연인과 함께 조용한 데이트를 즐기거나, 진솔한 대화를 나누며 서로를 더 깊이 이해할 수 있을 것입니다. "
                "싱글이라면 급하게 인연을 찾기보다는 자연스러운 만남을 기다리는 것이 좋습니다. "
                "주변 사람들과의 모임이나 취미 활동을 통해 새로운 인연을 만날 가능성도 있습니다. "
                "연애보다는 우정을 쌓는 데 집중하면 나중에 좋은 인연으로 발전할 수 있을 것입니다. "
                "오늘은 자신의 매력을 자연스럽게 발산하는 것이 중요한 날입니다."
            )
        else:
            texts['love'] = (
                "연애운이 다소 침체된 날이니 관계에서 신중한 태도가 필요합니다. "
                "사소한 오해나 다툼이 생길 수 있으니 말과 행동에 주의하고, 상대방의 입장을 이해하려는 노력이 필요합니다. "
                "연인과의 관계에서 잠시 거리를 두고 생각할 시간을 갖는 것도 도움이 될 수 있습니다. "
                "싱글이라면 오늘은 연애보다는 자기 자신에게 집중하는 시간을 가져보세요. "
                "자기 계발이나 취미 활동에 몰두하다 보면 자연스럽게 매력이 상승하고 좋은 인연을 만날 준비가 될 것입니다. "
                "어려운 시기를 잘 극복하면 더 좋은 사랑이 찾아올 것입니다."
            )
        
        # 학업운
        study_score = scores['study']
        if study_score >= 80:
            texts['study'] = (
                "학업운이 최상의 상태인 날입니다. 집중력과 이해력이 크게 향상되어 공부한 내용이 머릿속에 쏙쏙 들어올 것입니다. "
                "시험을 앞두고 있다면 오늘 집중적으로 공부하면 예상보다 좋은 결과를 얻을 수 있습니다. "
                "새로운 분야를 공부하기 시작하기에도 최적의 날이며, 어려웠던 개념도 쉽게 이해할 수 있을 것입니다. "
                "도서관이나 조용한 카페에서 공부하면 효율이 더욱 높아질 것입니다. "
                "오늘 공부한 내용은 오래 기억에 남을 것이니 중요한 내용 위주로 학습하는 것이 좋겠습니다. "
                "특히 오전 10시에서 12시 사이가 가장 집중력이 높은 시간대입니다."
            )
        elif study_score >= 60:
            texts['study'] = (
                "학업 면에서 꾸준한 진전을 보일 수 있는 안정적인 날입니다. "
                "어려운 문제에 도전하기보다는 기초를 다지고 복습하는 데 집중하면 좋은 성과를 얻을 수 있습니다. "
                "스터디 그룹이나 동료와의 토론을 통해 새로운 관점과 아이디어를 얻을 수 있을 것입니다. "
                "계획적으로 시간을 배분하여 공부하면 효율성을 높일 수 있으며, 적절한 휴식도 잊지 마세요. "
                "온라인 강의나 참고 자료를 활용하면 부족한 부분을 보완하는 데 도움이 될 것입니다. "
                "오늘은 꾸준함이 가장 중요한 열쇠가 될 것입니다."
            )
        else:
            texts['study'] = (
                "학업에 집중하기 어려운 날일 수 있으니 무리하지 말고 가벼운 복습 정도로 마무리하는 것이 좋습니다. "
                "어려운 과목보다는 관심 있는 분야나 쉬운 내용부터 시작하여 학습 동기를 유지하세요. "
                "오늘은 양보다 질에 집중하여 핵심 내용만 정리하는 것이 효과적일 것입니다. "
                "충분한 휴식과 수면을 취한 후 내일 다시 집중하는 것이 더 나은 선택일 수 있습니다. "
                "운동이나 산책을 통해 머리를 맑게 하면 학습 능력이 조금씩 회복될 것입니다. "
                "스트레스를 받지 말고 여유를 가지고 접근하는 것이 중요합니다."
            )
        
        # 직장운
        work_score = scores['work']
        if work_score >= 80:
            texts['work'] = (
                "직장운이 크게 상승하는 날로 당신의 능력이 인정받고 좋은 평가를 받을 수 있습니다. "
                "중요한 프로젝트나 발표가 있다면 자신감을 가지고 임하면 기대 이상의 성과를 낼 수 있을 것입니다. "
                "상사나 동료들과의 관계도 매우 원만하게 유지되며, 협업이 필요한 업무에서 시너지를 발휘할 수 있습니다. "
                "승진이나 인센티브 등의 좋은 소식을 들을 가능성도 있으니 기대해도 좋습니다. "
                "오늘의 성과는 앞으로의 커리어에 중요한 전환점이 될 수 있으니 최선을 다해 임하세요. "
                "특히 오후 2시에서 4시 사이에 중요한 기회가 찾아올 수 있습니다."
            )
        elif work_score >= 60:
            texts['work'] = (
                "업무가 순조롭게 진행되는 평온한 날입니다. 큰 성과는 없더라도 착실하게 맡은 일을 처리할 수 있을 것입니다. "
                "평소 미뤄두었던 서류 작업이나 정리가 필요한 업무를 처리하기에 좋은 시기입니다. "
                "동료들과의 소통과 협업이 원활하게 이루어지며, 팀워크를 발휘할 수 있을 것입니다. "
                "새로운 아이디어나 개선 사항이 있다면 상사에게 제안해보는 것도 좋은 기회가 될 수 있습니다. "
                "퇴근 후에는 자기 계발을 위한 시간을 가져보는 것도 미래를 위해 도움이 될 것입니다. "
                "오늘은 성실함과 꾸준함이 가장 중요한 덕목입니다."
            )
        else:
            texts['work'] = (
                "직장에서 작은 어려움이나 스트레스가 있을 수 있는 날입니다. "
                "중요한 결정이나 새로운 시도는 미루고, 기존 업무에 집중하는 것이 안전합니다. "
                "실수를 방지하기 위해 평소보다 꼼꼼히 확인하고, 이중 체크하는 습관을 가지세요. "
                "동료나 상사와의 의견 충돌이 있을 수 있으니 감정적으로 대응하지 말고 냉정을 유지하는 것이 중요합니다. "
                "오늘은 눈에 띄는 성과보다는 실수를 줄이고 안정적으로 하루를 마무리하는 데 집중하세요. "
                "어려운 시기는 곧 지나갈 것이니 인내심을 가지고 견뎌내세요."
            )

        # 건강운
        health_score = scores.get('health', 70)
        if health_score >= 80:
            texts['health'] = (
                "건강운이 매우 좋은 날입니다. 몸과 마음 모두 활력이 넘치며 평소보다 에너지가 넘칠 것입니다. "
                "운동을 시작하거나 새로운 건강 습관을 들이기에 최적의 시기입니다. "
                "오전에 가벼운 스트레칭이나 조깅을 하면 하루 종일 상쾌한 기분을 유지할 수 있습니다. "
                "면역력도 좋은 상태이니 평소 미뤄왔던 야외 활동이나 스포츠를 즐겨보세요. "
                "충분한 수분 섭취와 균형 잡힌 식사를 병행하면 건강이 더욱 좋아질 것입니다. "
                "오늘의 좋은 컨디션을 유지하기 위해 규칙적인 생활 패턴을 이어가세요."
            )
        elif health_score >= 60:
            texts['health'] = (
                "건강운이 안정적인 날입니다. 큰 문제는 없지만 자기 관리에 신경 쓰면 더 좋아질 수 있습니다. "
                "규칙적인 식사와 적당한 운동이 건강 유지의 핵심이 될 것입니다. "
                "장시간 앉아있는 것은 피하고, 틈틈이 스트레칭을 해주는 것이 좋습니다. "
                "카페인이나 자극적인 음식은 자제하고, 따뜻한 차나 물을 자주 마시세요. "
                "피로가 쌓이지 않도록 충분한 수면을 취하고, 스트레스 관리에도 신경 쓰세요. "
                "오늘은 무리하지 않고 자신의 페이스를 유지하는 것이 중요합니다."
            )
        else:
            texts['health'] = (
                "건강 관리에 특별히 주의가 필요한 날입니다. 무리한 활동은 피하고 충분한 휴식을 취하세요. "
                "면역력이 다소 떨어져 있을 수 있으니 손 씻기와 개인 위생에 신경 써주세요. "
                "소화가 잘 안 될 수 있으니 기름진 음식보다는 담백하고 따뜻한 음식을 선택하세요. "
                "두통이나 피로감이 느껴진다면 잠시 눈을 감고 휴식을 취하는 것이 좋습니다. "
                "격한 운동보다는 가벼운 산책이나 요가 같은 저강도 활동이 적합합니다. "
                "오늘은 몸의 신호에 귀 기울이고, 자신을 돌보는 시간을 가져보세요."
            )

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
    
