"""
운세 계산 메인 클래스 - 각 서비스를 조합하여 운세 계산
"""
import random
import hashlib
from datetime import date, datetime
from typing import Dict, Optional

from django.conf import settings

from ..saju_calculator import SajuCalculator
from ..lunar_converter import lunar_to_solar
from .zodiac_service import ZodiacService
from .color_service import ColorService
from .lotto_service import LottoService
from .item_service import ItemService
from .score_service import ScoreService
from .text_service import TextService


class FortuneCalculator:
    """운세 계산 메인 클래스 - 책임을 각 서비스에 위임"""

    def __init__(self):
        self.cache_ttl = getattr(settings, 'CACHE_TTL', 86400)
        self.saju_calc = SajuCalculator()

        # 서비스 초기화
        self.zodiac_service = ZodiacService(self.saju_calc)
        self.color_service = ColorService()
        self.lotto_service = LottoService()
        self.item_service = ItemService()
        self.score_service = ScoreService()
        self.text_service = TextService()

    def calculate_fortune(
        self,
        birth_date: date,
        gender: str,
        birth_time: Optional[datetime] = None,
        chinese_name: Optional[str] = None,
        mbti: Optional[str] = None,
        personal_color: Optional[str] = None,
        calendar_type: str = 'solar',
        user_id: Optional[int] = None,
        session_key: Optional[str] = None,
        fortune_seed: Optional[str] = None,
        period_type: str = 'daily'
    ) -> Dict:
        """운세 계산 메인 함수"""
        # 음력인 경우 양력으로 변환
        original_birth_date = birth_date
        if calendar_type == 'lunar':
            solar_date = lunar_to_solar(birth_date)
            if solar_date:
                birth_date = solar_date
                print(f"[DEBUG] 음력 {original_birth_date} -> 양력 {birth_date} 변환")
            else:
                print(f"[WARNING] 음력 변환 실패, 원본 날짜 사용")

        today = date.today()

        # 고유 시드 생성
        if fortune_seed:
            seed_string = f"{fortune_seed}-{birth_date.isoformat()}-{gender}"
        else:
            seed_string = f"{today.isoformat()}-{birth_date.isoformat()}-{gender}"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
        random.seed(seed)

        # 사주 데이터 계산
        saju_data = self.zodiac_service.calculate_saju(birth_date, birth_time)

        # 각 운별 점수 계산
        fortune_scores = self.score_service.calculate_all_fortunes(birth_date, today, saju_data)

        # 별자리 계산
        zodiac_sign = self.zodiac_service.get_zodiac_sign(birth_date)

        # 띠 계산
        if calendar_type == 'lunar':
            chinese_zodiac = self.zodiac_service.get_chinese_zodiac_lunar(original_birth_date)
        else:
            chinese_zodiac = self.zodiac_service.get_chinese_zodiac(birth_date)

        # 행운의 색상들 결정
        lucky_colors = self.color_service.determine_lucky_colors(
            zodiac_sign, chinese_zodiac, today, fortune_scores, personal_color
        )

        # 로또 번호 생성
        lotto_numbers = self.lotto_service.generate_lucky_numbers(
            birth_date, today, fortune_scores, gender, user_id, session_key
        )

        # 행운의 아이템 결정
        lucky_item = self.item_service.determine_lucky_item(
            zodiac_sign, today, user_id, session_key, lucky_colors,
            fortune_score=fortune_scores['total'],
            fortune_scores=fortune_scores
        )

        # 상세 운세 텍스트 생성 (LLM 시도 후 실패시 기존 로직)
        fortune_texts = self.text_service.generate_fortune_text_with_llm(
            birth_date, gender, saju_data, zodiac_sign, chinese_zodiac, fortune_scores, mbti,
            lucky_item['main'], lucky_item['zodiac'], period_type
        )

        if fortune_texts:
            if 'scores' in fortune_texts:
                del fortune_texts['scores']
            print(f"[DEBUG] 자체 계산 점수 사용: {fortune_scores}")
        else:
            print("[DEBUG] LLM 생성 실패, 기존 로직 사용")
            fortune_texts = self.text_service.generate_fortune_texts_fallback(
                fortune_scores, zodiac_sign, chinese_zodiac, period_type
            )

        return {
            'fortune_score': fortune_scores['total'],
            'fortune_scores': fortune_scores,
            'fortune_texts': fortune_texts,
            'saju_data': saju_data,
            'zodiac_sign': zodiac_sign,
            'chinese_zodiac': chinese_zodiac,
            'lucky_color': lucky_colors[0] if lucky_colors else '파란색',
            'lucky_colors': lucky_colors,
            'lotto_numbers': lotto_numbers,
            'lucky_item': lucky_item,
            'calculation_date': today.isoformat(),
            'birth_date': birth_date.isoformat(),
            'gender': gender,
            'user_id': user_id,
            'session_key': session_key,
            'mbti': mbti
        }

    # 기존 호환성을 위한 메서드들 (위임)
    def _calculate_saju(self, birth_date: date, birth_time: Optional[datetime] = None) -> Dict:
        return self.zodiac_service.calculate_saju(birth_date, birth_time)

    def _get_zodiac_sign(self, birth_date: date) -> str:
        return self.zodiac_service.get_zodiac_sign(birth_date)

    def _get_chinese_zodiac(self, birth_date: date) -> str:
        return self.zodiac_service.get_chinese_zodiac(birth_date)

    def _get_chinese_zodiac_lunar(self, lunar_date: date) -> str:
        return self.zodiac_service.get_chinese_zodiac_lunar(lunar_date)

    def _calculate_all_fortunes(self, birth_date: date, today: date, saju_data: Dict = None) -> Dict:
        return self.score_service.calculate_all_fortunes(birth_date, today, saju_data)

    def _determine_lucky_colors(self, zodiac_sign: str, chinese_zodiac: str, today: date,
                                fortune_scores: Dict = None, personal_color: Optional[str] = None):
        return self.color_service.determine_lucky_colors(
            zodiac_sign, chinese_zodiac, today, fortune_scores, personal_color
        )

    def _generate_lucky_lotto_numbers(self, birth_date: date, today: date, fortune_scores: Dict = None,
                                       gender: str = None, user_id: int = None, session_key: str = None):
        return self.lotto_service.generate_lucky_numbers(
            birth_date, today, fortune_scores, gender, user_id, session_key
        )

    def _determine_lucky_item(self, zodiac_sign: str, today: date, user_id: int = None,
                              session_key: str = None, lucky_colors=None, fortune_score: int = 70,
                              fortune_scores: Dict = None) -> Dict:
        return self.item_service.determine_lucky_item(
            zodiac_sign, today, user_id, session_key, lucky_colors, fortune_score, fortune_scores
        )

    def _generate_fortune_text_with_llm(self, *args, **kwargs):
        return self.text_service.generate_fortune_text_with_llm(*args, **kwargs)

    def _generate_fortune_texts(self, scores: Dict, zodiac_sign: str, chinese_zodiac: str, period_type: str = 'daily'):
        return self.text_service.generate_fortune_texts_fallback(scores, zodiac_sign, chinese_zodiac, period_type)
