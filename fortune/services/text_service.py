"""
운세 텍스트 생성 서비스 (LLM + 폴백)
"""
import json
import random
from datetime import date
from typing import Dict, Optional

from django.core.cache import cache
from django.conf import settings

from .notification_service import send_api_quota_alert


class TextService:
    """운세 텍스트 생성 서비스"""

    MBTI_GUIDES = {
        'INTJ': '논리적이고 분석적인 톤. 효율성과 장기 계획 관점에서 조언. 솔직하고 직접적으로.',
        'INTP': '지적 호기심을 자극하는 톤. 다양한 가능성과 아이디어 관점에서. 유연하게.',
        'ENTJ': '자신감 있고 추진력 있는 톤. 목표 달성과 리더십 관점에서. 결단력 있게.',
        'ENTP': '창의적이고 도전적인 톤. 새로운 기회와 가능성에 초점. 열정적으로.',
        'INFJ': '따뜻하고 통찰력 있는 톤. 의미와 가치 관점에서 조언. 깊이 있게.',
        'INFP': '감성적이고 진솔한 톤. 개인의 가치와 성장 관점에서. 부드럽게.',
        'ENFJ': '격려하고 동기부여하는 톤. 관계와 조화 관점에서. 따뜻하고 적극적으로.',
        'ENFP': '열정적이고 긍정적인 톤. 가능성과 영감 관점에서. 밝고 활기차게.',
        'ISTJ': '신뢰감 있고 안정적인 톤. 책임과 실용성 관점에서. 체계적으로.',
        'ISFJ': '배려심 있고 따뜻한 톤. 안전과 조화 관점에서. 세심하게.',
        'ESTJ': '명확하고 실행 지향적 톤. 효율과 결과 관점에서. 단호하게.',
        'ESFJ': '친절하고 협조적인 톤. 관계와 화합 관점에서. 배려하며.',
        'ISTP': '실용적이고 간결한 톤. 문제 해결과 자유 관점에서. 직설적으로.',
        'ISFP': '부드럽고 자연스러운 톤. 감각과 현재의 즐거움 관점에서. 온화하게.',
        'ESTP': '역동적이고 현실적인 톤. 행동과 즉각적 결과 관점에서. 활발하게.',
        'ESFP': '밝고 사교적인 톤. 재미와 즐거움 관점에서. 유쾌하게.',
    }

    def get_mbti_tone_guide(self, mbti: Optional[str]) -> str:
        """MBTI에 따른 톤 가이드 반환"""
        if not mbti or mbti.upper() not in self.MBTI_GUIDES:
            return ""
        return f"\n[MBTI 맞춤 스타일]\nMBTI {mbti.upper()}: {self.MBTI_GUIDES[mbti.upper()]}"

    def combine_period_fortune_text(self, result: Dict, period_type: str) -> Dict:
        """주간/월간 운세의 시간대별 개별 필드를 하나의 텍스트로 조합"""
        combined = {}
        fortune_types = ['total', 'money', 'love', 'study', 'work', 'health']

        if period_type == 'weekly':
            time_keys = ['summary', 'early_week', 'late_week', 'weekend', 'advice']
            time_labels = ['', '평일 초(월~화)에는 ', '평일 말(수~금)에는 ', '주말(토~일)에는 ', '']
        else:  # monthly
            time_keys = ['summary', 'early_month', 'mid_month', 'late_month', 'advice']
            time_labels = ['', '월초(1~10일)에는 ', '월중(11~20일)에는 ', '월말(21일~)에는 ', '']

        for fortune_type in fortune_types:
            if fortune_type in result and isinstance(result[fortune_type], dict):
                parts = []
                for key, label in zip(time_keys, time_labels):
                    if key in result[fortune_type]:
                        text = result[fortune_type][key]
                        if label and not text.startswith(label):
                            text = label + text
                        parts.append(text)
                combined[fortune_type] = ' '.join(parts)
            elif fortune_type in result:
                combined[fortune_type] = result[fortune_type]

        if 'lucky_item' in result:
            combined['lucky_item'] = result['lucky_item']

        return combined

    def build_fortune_prompt(
        self,
        birth_date: date,
        gender: str,
        zodiac: str,
        chinese_zodiac: str,
        mbti_info: str,
        lucky_item_info: str,
        saju: Dict,
        lucky_item_name: str,
        zodiac_item_name: str,
        period_type: str = 'daily',
        scores: Dict = None,
        mbti: Optional[str] = None
    ) -> str:
        """기간 유형에 따른 운세 프롬프트 생성"""
        today = date.today()
        mbti_guide = self.get_mbti_tone_guide(mbti)

        if period_type == 'weekly':
            return self._build_weekly_prompt(
                birth_date, gender, zodiac, chinese_zodiac, mbti_info,
                lucky_item_info, saju, lucky_item_name, zodiac_item_name, today, mbti_guide
            )
        elif period_type == 'monthly':
            return self._build_monthly_prompt(
                birth_date, gender, zodiac, chinese_zodiac, mbti_info,
                lucky_item_info, saju, lucky_item_name, zodiac_item_name, today, mbti_guide
            )
        else:
            return self._build_daily_prompt(
                birth_date, gender, zodiac, chinese_zodiac, mbti_info,
                lucky_item_info, saju, lucky_item_name, zodiac_item_name, today, mbti_guide
            )

    def _build_weekly_prompt(self, birth_date, gender, zodiac, chinese_zodiac, mbti_info,
                             lucky_item_info, saju, lucky_item_name, zodiac_item_name, today, mbti_guide):
        return f"""당신은 전문 운세 상담가입니다. 아래 사용자의 정보를 바탕으로 '이번 주의 운세'를 작성해주세요.

[사용자 정보]
- 생년월일: {birth_date}
- 성별: {'남성' if gender == 'M' else '여성'}
- 별자리: {zodiac}
- 띠: {chinese_zodiac}
{mbti_info}
{lucky_item_info}
- 사주: {saju['year']}년 {saju['month']}월 {saju['day']}일 {saju['hour']}시
- 현재 날짜: {today}
{mbti_guide}

[중요 - 반드시 지켜야 할 JSON 구조]
각 운세 항목(total, money, love, study, work, health)은 반드시 아래 5개 필드를 가진 객체여야 합니다:
- "summary": 이번 주 전체 요약 (1문장)
- "early_week": 월요일~화요일 운세 (1문장, 다른 시간대와 완전히 다른 내용)
- "late_week": 수요일~금요일 운세 (1문장, 다른 시간대와 완전히 다른 내용)
- "weekend": 토요일~일요일 운세 (1문장, 다른 시간대와 완전히 다른 내용)
- "advice": 이번 주 조언 (1문장)

[작성 가이드]
1. 말투: "~합니다", "~입니다" 체의 정중한 문체
2. 행운의 아이템:
   - '{lucky_item_name}' 설명: 2문장
   - '{zodiac_item_name}' 설명: 2문장

반드시 아래 JSON 구조로 출력하세요:
{{
    "total": {{"summary": "...", "early_week": "...", "late_week": "...", "weekend": "...", "advice": "..."}},
    "money": {{"summary": "...", "early_week": "...", "late_week": "...", "weekend": "...", "advice": "..."}},
    "love": {{"summary": "...", "early_week": "...", "late_week": "...", "weekend": "...", "advice": "..."}},
    "study": {{"summary": "...", "early_week": "...", "late_week": "...", "weekend": "...", "advice": "..."}},
    "work": {{"summary": "...", "early_week": "...", "late_week": "...", "weekend": "...", "advice": "..."}},
    "health": {{"summary": "...", "early_week": "...", "late_week": "...", "weekend": "...", "advice": "..."}},
    "lucky_item": {{"description": "...", "zodiac_description": "..."}}
}}"""

    def _build_monthly_prompt(self, birth_date, gender, zodiac, chinese_zodiac, mbti_info,
                              lucky_item_info, saju, lucky_item_name, zodiac_item_name, today, mbti_guide):
        return f"""당신은 전문 운세 상담가입니다. 아래 사용자의 정보를 바탕으로 '이번 달의 운세'를 작성해주세요.

[사용자 정보]
- 생년월일: {birth_date}
- 성별: {'남성' if gender == 'M' else '여성'}
- 별자리: {zodiac}
- 띠: {chinese_zodiac}
{mbti_info}
{lucky_item_info}
- 사주: {saju['year']}년 {saju['month']}월 {saju['day']}일 {saju['hour']}시
- 현재 날짜: {today}
{mbti_guide}

[중요 - 반드시 지켜야 할 JSON 구조]
각 운세 항목(total, money, love, study, work, health)은 반드시 아래 5개 필드를 가진 객체여야 합니다:
- "summary": 이번 달 전체 요약 (1문장)
- "early_month": 1~10일 운세 (1문장, 다른 시간대와 완전히 다른 내용)
- "mid_month": 11~20일 운세 (1문장, 다른 시간대와 완전히 다른 내용)
- "late_month": 21일~ 운세 (1문장, 다른 시간대와 완전히 다른 내용)
- "advice": 이번 달 조언 (1문장)

[작성 가이드]
1. 말투: "~합니다", "~입니다" 체의 정중한 문체
2. 행운의 아이템:
   - '{lucky_item_name}' 설명: 2문장
   - '{zodiac_item_name}' 설명: 2문장

반드시 아래 JSON 구조로 출력하세요:
{{
    "total": {{"summary": "...", "early_month": "...", "mid_month": "...", "late_month": "...", "advice": "..."}},
    "money": {{"summary": "...", "early_month": "...", "mid_month": "...", "late_month": "...", "advice": "..."}},
    "love": {{"summary": "...", "early_month": "...", "mid_month": "...", "late_month": "...", "advice": "..."}},
    "study": {{"summary": "...", "early_month": "...", "mid_month": "...", "late_month": "...", "advice": "..."}},
    "work": {{"summary": "...", "early_month": "...", "mid_month": "...", "late_month": "...", "advice": "..."}},
    "health": {{"summary": "...", "early_month": "...", "mid_month": "...", "late_month": "...", "advice": "..."}},
    "lucky_item": {{"description": "...", "zodiac_description": "..."}}
}}"""

    def _build_daily_prompt(self, birth_date, gender, zodiac, chinese_zodiac, mbti_info,
                            lucky_item_info, saju, lucky_item_name, zodiac_item_name, today, mbti_guide):
        return f"""당신은 전문 운세 상담가입니다. 아래 사용자의 정보를 바탕으로 '오늘의 운세'를 작성해주세요.

[사용자 정보]
- 생년월일: {birth_date}
- 성별: {'남성' if gender == 'M' else '여성'}
- 별자리: {zodiac}
- 띠: {chinese_zodiac}
{mbti_info}
{lucky_item_info}
- 사주: {saju['year']}년 {saju['month']}월 {saju['day']}일 {saju['hour']}시
- 현재 날짜: {today}
{mbti_guide}

[작성 가이드]
1. 각 운세 항목(총운, 재물, 애정, 학업, 직장, 건강)을 5문장으로 작성
2. 첫 문장은 전반적 개요, 마지막 문장은 조언
3. 중간 3문장은 구체적 상황 (오전/오후/저녁 시간대 활용)
4. 말투: "~합니다", "~입니다" 체의 정중한 문체
5. 행운의 아이템:
   - '{lucky_item_name}' 설명: 2문장
   - '{zodiac_item_name}' 설명: 2문장

반드시 아래 JSON 구조로 출력하세요:
{{
    "total": "총운 내용 5문장...",
    "money": "재물운 내용 5문장...",
    "love": "애정운 내용 5문장...",
    "study": "학업운 내용 5문장...",
    "work": "직장운 내용 5문장...",
    "health": "건강운 내용 5문장...",
    "lucky_item": {{"description": "...", "zodiac_description": "..."}}
}}"""

    def generate_fortune_text_with_llm(
        self,
        birth_date: date,
        gender: str,
        saju: Dict,
        zodiac: str,
        chinese_zodiac: str,
        scores: Dict,
        mbti: Optional[str] = None,
        lucky_item_name: Optional[str] = None,
        zodiac_item_name: Optional[str] = None,
        period_type: str = 'daily'
    ) -> Optional[Dict]:
        """Gemini API를 사용한 운세 텍스트 생성"""
        import time
        import google.generativeai as genai

        cache_key = f"fortune_text_v6_{birth_date}_{gender}_{zodiac}_{chinese_zodiac}_{mbti}_{lucky_item_name}_{date.today()}_{period_type}"
        cached_result = cache.get(cache_key)

        if cached_result:
            print("[DEBUG] 캐시된 운세 텍스트 사용")
            return cached_result

        gemini_api_key = getattr(settings, 'GEMINI_API_KEY', '')

        if not gemini_api_key:
            print("[ERROR] GEMINI_API_KEY가 설정되지 않음")
            return None

        max_retries = 1
        retry_delay = 2

        mbti_info = f"- MBTI: {mbti}" if mbti else "- MBTI: 정보 없음"
        lucky_item_info = f"- 운세 기반 행운 아이템: {lucky_item_name}" if lucky_item_name else ""

        prompt = self.build_fortune_prompt(
            birth_date, gender, zodiac, chinese_zodiac, mbti_info, lucky_item_info,
            saju, lucky_item_name, zodiac_item_name, period_type, scores, mbti
        )

        system_msg = self._get_system_message(period_type)

        for attempt in range(max_retries + 1):
            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

                print(f"[DEBUG] Gemini API gemini-2.5-flash 운세 생성 요청 (시도: {attempt + 1}/{max_retries + 1})...")

                full_prompt = f"{system_msg}\n\n{prompt}"
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.85,
                        max_output_tokens=2500
                    )
                )

                text = response.text.strip()

                if text.startswith('```json'):
                    text = text[7:]
                if text.startswith('```'):
                    text = text[3:]
                if text.endswith('```'):
                    text = text[:-3]

                result = json.loads(text.strip())
                print("[DEBUG] Gemini API gemini-2.5-flash 운세 생성 성공!")

                if period_type in ['weekly', 'monthly']:
                    result = self.combine_period_fortune_text(result, period_type)

                cache.set(cache_key, result, 60 * 60 * 24)
                return result

            except Exception as e:
                error_str = str(e)
                print(f"[ERROR] Gemini API gemini-2.5-flash 운세 생성 오류 (시도: {attempt + 1}): {e}")

                if 'insufficient_quota' in error_str or '429' in error_str or 'quota' in error_str.lower():
                    send_api_quota_alert('Gemini API (gemini-2.5-flash)', error_str)

                if attempt < max_retries:
                    time.sleep(retry_delay)
                continue

        print("[ERROR] Gemini API 시도 실패, 동적 텍스트 생성으로 대체")
        return None

    def _get_system_message(self, period_type: str) -> str:
        """기간 유형에 따른 시스템 메시지 반환"""
        if period_type == 'weekly':
            return """당신은 주간 운세 전문가입니다.
반드시 각 운세 항목을 5문장으로 작성하되:
- 2번째 문장은 "평일 초(월~화)에는 "로 시작
- 3번째 문장은 "평일 말(수~금)에는 "로 시작
- 4번째 문장은 "주말(토~일)에는 "로 시작
이 형식을 어기면 잘못된 응답입니다."""
        elif period_type == 'monthly':
            return """당신은 월간 운세 전문가입니다.
반드시 각 운세 항목을 5문장으로 작성하되:
- 2번째 문장은 "월초(1~10일)에는 "로 시작
- 3번째 문장은 "월중(11~20일)에는 "로 시작
- 4번째 문장은 "월말(21일~)에는 "로 시작
이 형식을 어기면 잘못된 응답입니다."""
        else:
            return "당신은 일일 운세 전문가입니다. 오전/오후/저녁 시간대를 활용하여 운세를 작성하세요."

    def generate_fortune_texts_fallback(
        self,
        scores: Dict,
        zodiac_sign: str,
        chinese_zodiac: str,
        period_type: str = 'daily'
    ) -> Dict:
        """LLM 실패 시 동적 운세 텍스트 생성 - 날짜/점수 기반 변형"""
        today = date.today()
        day_seed = today.toordinal() + hash(zodiac_sign) % 100
        random.seed(day_seed)

        time_expressions = self._get_time_expressions(period_type)
        texts = {}

        texts['total'] = self._generate_total_fortune(scores['total'], time_expressions)
        texts['money'] = self._generate_money_fortune(scores['money'], time_expressions)
        texts['love'] = self._generate_love_fortune(scores['love'], time_expressions)
        texts['study'] = self._generate_study_fortune(scores['study'], time_expressions)
        texts['work'] = self._generate_work_fortune(scores['work'], time_expressions)
        texts['health'] = self._generate_health_fortune(scores.get('health', 70), time_expressions)

        # 주간/월간 운세인 경우 텍스트 치환
        if period_type != 'daily':
            for key in texts:
                if texts[key]:
                    texts[key] = texts[key].replace('오늘', time_expressions['period_word'])
                    texts[key] = texts[key].replace('하루', time_expressions['period_unit'])
                    texts[key] = texts[key].replace('내일', f"{time_expressions['period_word']} 이후")

        random.seed()
        return texts

    def _get_time_expressions(self, period_type: str) -> Dict:
        """기간 유형에 따른 시간 표현 반환"""
        if period_type == 'weekly':
            return {
                'morning': random.choice(["주 초반", "이번 주 초", "주간 전반부", "평일 초반"]),
                'afternoon': random.choice(["주 중반", "수요일 무렵", "주간 중반부", "평일 중반"]),
                'evening': random.choice(["주 후반", "금요일 무렵", "주말 전", "이번 주 말"]),
                'period_word': "이번 주",
                'period_unit': "한 주"
            }
        elif period_type == 'monthly':
            return {
                'morning': random.choice(["월초", "이번 달 초", "달의 전반부", "초순"]),
                'afternoon': random.choice(["월중반", "달의 중반", "중순 무렵", "보름 무렵"]),
                'evening': random.choice(["월말", "이번 달 말", "달의 후반부", "하순"]),
                'period_word': "이번 달",
                'period_unit': "한 달"
            }
        else:
            return {
                'morning': random.choice(["오전 9시", "오전 10시", "오전 11시", "아침 일찍"]),
                'afternoon': random.choice(["오후 2시", "오후 3시", "오후 4시", "점심 이후"]),
                'evening': random.choice(["저녁 6시", "저녁 7시", "저녁 8시", "저녁 무렵"]),
                'period_word': "오늘",
                'period_unit': "하루"
            }

    def _generate_total_fortune(self, score: int, time: Dict) -> str:
        action_pos = random.choice(["적극적으로", "자신감 있게", "주도적으로", "과감하게"])
        action_neu = random.choice(["차분하게", "꾸준히", "성실하게", "묵묵히"])
        action_neg = random.choice(["신중하게", "조심스럽게", "천천히", "여유롭게"])

        if score >= 80:
            return f"오늘은 전반적으로 운기가 상승하는 날입니다. {time['morning']}부터 긍정적인 에너지가 느껴지며, 평소 미뤄둔 일들을 처리하기 좋습니다. 주변 사람들과의 관계에서도 좋은 일이 생길 가능성이 높으니, {action_pos} 행동해 보세요. {time['afternoon']}에는 예상치 못한 기쁜 소식을 들을 수도 있습니다. 오늘의 좋은 기운을 최대한 활용하여 중요한 일을 추진해 보세요."
        elif score >= 60:
            return f"안정적인 기운이 감도는 하루입니다. 큰 변화보다는 {action_neu} 일상을 보내는 것이 좋으며, 급한 결정은 피하는 것이 현명합니다. {time['morning']}에는 가벼운 운동이나 산책으로 하루를 시작하면 좋겠습니다. 오후에는 밀린 업무나 집안일을 정리하기에 적합한 시간입니다. 소소한 일상에서 행복을 찾아보세요."
        else:
            return f"오늘은 {action_neg} 움직이는 것이 좋겠습니다. 무리한 계획이나 새로운 시도는 피하고, 기존에 하던 일에 집중하세요. 컨디션이 평소보다 떨어질 수 있으니 충분한 휴식을 취하는 것이 중요합니다. {time['evening']}에는 일찍 귀가하여 편안한 시간을 보내세요. 내일은 더 나은 기운이 찾아올 것입니다."

    def _generate_money_fortune(self, score: int, time: Dict) -> str:
        if score >= 80:
            return f"재물운이 좋은 날입니다. 예상치 못한 수입이나 좋은 거래가 성사될 가능성이 있습니다. {time['afternoon']}에 금전적으로 좋은 소식을 들을 수 있으며, 소소한 투자도 괜찮은 결과를 가져올 수 있습니다. 다만 과욕은 금물이니 적당한 선에서 만족하세요. 오늘 들어온 재물은 일부 저축하는 것이 좋겠습니다."
        elif score >= 60:
            return f"재물운이 안정적인 날입니다. 큰 수입은 없지만 지출도 적을 것입니다. 계획적인 소비를 하면 무난한 하루를 보낼 수 있으며, 미래를 위한 저축을 시작하기 좋은 때입니다. 불필요한 충동구매는 자제하고, 꼭 필요한 것만 구입하세요. 작은 절약이 큰 재물을 만듭니다."
        else:
            return f"재물운이 다소 저조한 날입니다. 충동구매나 불필요한 지출을 자제하고, 계획에 없던 소비는 최대한 피하세요. 투자나 도박성 거래는 절대 피해야 하며, 금전 대출이나 보증도 서지 않는 것이 좋습니다. 어려운 시기는 곧 지나갈 것입니다. 내일을 위해 오늘은 아끼세요."

    def _generate_love_fortune(self, score: int, time: Dict) -> str:
        if score >= 80:
            return f"연애운이 빛나는 날입니다. 싱글이라면 매력적인 이성을 만날 기회가 있으며, {time['evening']}에 특별한 인연이 찾아올 수 있습니다. 연인이 있다면 깊은 대화와 함께 관계가 더욱 돈독해질 것입니다. 상대방에 대한 작은 배려가 큰 감동을 줄 수 있는 날입니다. 사랑하는 마음을 표현하는 것을 두려워하지 마세요."
        elif score >= 60:
            return f"연애운이 평온한 날입니다. 큰 변화보다는 일상의 소소한 애정 표현이 중요합니다. 연인과 함께 조용한 시간을 보내거나, 진솔한 대화를 나눠보세요. 싱글이라면 자연스러운 만남을 기다리는 것이 좋습니다. 무리하게 인연을 찾기보다 자기 자신을 가꾸는 시간을 가지세요."
        else:
            return f"연애운이 다소 침체된 날입니다. 연인과의 사소한 오해나 다툼에 주의하고, 감정적인 대화는 피하는 것이 좋습니다. 싱글이라면 오늘은 자기 자신에게 집중하는 시간을 가져보세요. 자기 계발에 투자하면 나중에 더 좋은 인연이 찾아올 것입니다. 내면의 성장이 외적인 매력으로 이어집니다."

    def _generate_study_fortune(self, score: int, time: Dict) -> str:
        action_neu = random.choice(["차분하게", "꾸준히", "성실하게", "묵묵히"])
        action_neg = random.choice(["신중하게", "조심스럽게", "천천히", "여유롭게"])
        places = random.choice(["카페", "공원", "도서관", "익숙한 장소"])

        if score >= 80:
            return f"학업운이 최상인 날입니다. 집중력이 크게 향상되어 {time['morning']}부터 {time['afternoon']}까지가 황금 시간대입니다. 어려웠던 개념도 쉽게 이해할 수 있으며, 새로운 공부를 시작하기에도 좋습니다. {places}에서 공부하면 효율이 더욱 높아질 것입니다. 오늘 공부한 내용은 오래도록 기억에 남을 것입니다."
        elif score >= 60:
            return f"학업에 있어 안정적인 흐름입니다. 새로운 것보다는 복습에 집중하면 좋은 성과를 얻을 수 있습니다. 동료나 스터디 그룹과의 토론도 도움이 됩니다. {action_neu} 공부하는 것이 효과적입니다. 하루 목표를 정하고 차근차근 진행해보세요."
        else:
            return f"학업에 집중하기 어려운 날일 수 있습니다. 무리하지 말고 가벼운 복습 위주로 하루를 마무리하세요. 피곤함이 느껴진다면 충분한 휴식을 취한 후 다시 시작하는 것이 낫습니다. {action_neg} 접근하세요. 내일 더 좋은 컨디션으로 공부할 수 있을 것입니다."

    def _generate_work_fortune(self, score: int, time: Dict) -> str:
        action_pos = random.choice(["적극적으로", "자신감 있게", "주도적으로", "과감하게"])
        action_neu = random.choice(["차분하게", "꾸준히", "성실하게", "묵묵히"])
        action_neg = random.choice(["신중하게", "조심스럽게", "천천히", "여유롭게"])

        if score >= 80:
            return f"직장운이 상승하는 날입니다. 당신의 능력과 노력이 인정받을 가능성이 높으며, {time['afternoon']}에 좋은 소식을 들을 수 있습니다. 중요한 미팅이나 발표가 있다면 자신감을 가지고 임하세요. 동료들과의 협업도 원활하게 이루어질 것입니다. 오늘의 성과가 앞으로의 커리어에 좋은 영향을 줄 것입니다."
        elif score >= 60:
            return f"업무가 무난하게 흘러가는 날입니다. 큰 성과는 없더라도 맡은 일을 {action_neu} 처리하면 됩니다. 미뤄둔 업무를 정리하기 좋은 때이며, 동료들과 원활한 소통이 가능합니다. 오늘은 기초를 다지는 시간으로 삼으면 좋겠습니다. 작은 일도 성실하게 처리하는 모습이 신뢰를 쌓아줍니다."
        else:
            return f"직장에서 {action_neg} 행동하는 것이 좋겠습니다. 중요한 결정이나 새로운 제안은 미루고, 평소 하던 일에만 집중하세요. 동료나 상사와의 의견 충돌에 주의하고, 감정적인 대응은 피하세요. 오늘은 묵묵히 주어진 일만 처리하는 것이 현명합니다. 내일 더 좋은 기회가 찾아올 것입니다."

    def _generate_health_fortune(self, score: int, time: Dict) -> str:
        if score >= 80:
            return f"건강운이 좋은 날입니다. 몸과 마음 모두 활력이 넘치며, 새로운 운동을 시작하기에 좋은 시기입니다. {time['morning']}에 가벼운 운동으로 하루를 시작하면 상쾌한 기분이 종일 유지될 것입니다. 충분한 수분 섭취도 잊지 마세요. 오늘의 활력이 내일까지 이어질 것입니다."
        elif score >= 60:
            return f"건강운이 안정적인 날입니다. 무리하지 않는 선에서 규칙적인 생활을 유지하면 좋겠습니다. 가벼운 스트레칭이나 산책이 도움이 되며, 충분한 수면도 중요합니다. 음식은 소화가 잘 되는 것 위주로 드시세요. 몸과 마음의 균형을 유지하는 것이 중요합니다."
        else:
            return f"건강 관리에 신경 써야 하는 날입니다. 무리한 활동은 피하고, {time['evening']}에는 일찍 휴식을 취하세요. 소화가 안 될 수 있으니 가벼운 음식 위주로 드시고, 충분한 수면이 필요합니다. 몸이 보내는 신호에 귀 기울이세요. 오늘 쉬어야 내일 더 건강해집니다."
