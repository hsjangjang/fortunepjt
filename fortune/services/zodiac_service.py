"""
별자리/띠/사주 계산 서비스
"""
from datetime import date, datetime
from typing import Dict, Optional


class ZodiacService:
    """별자리, 띠, 사주 계산 서비스"""

    def __init__(self, saju_calculator=None):
        self.saju_calc = saju_calculator

    def calculate_saju(self, birth_date: date, birth_time: Optional[datetime] = None) -> Dict:
        """사주 계산 (정확한 만세력 기준)"""
        if self.saju_calc:
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

        return self._calculate_saju_fallback(birth_date, birth_time)

    def _calculate_saju_fallback(self, birth_date: date, birth_time: Optional[datetime] = None) -> Dict:
        """사주 계산 폴백 (간단 계산)"""
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

    def get_zodiac_sign(self, birth_date: date) -> str:
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

    def get_chinese_zodiac(self, birth_date: date) -> str:
        """띠 계산 (입춘 기준 - 양력용)"""
        year = birth_date.year

        if self.saju_calc:
            ipchun = self.saju_calc._get_ipchun_date(year)
            if birth_date < ipchun:
                year -= 1

        zodiacs = ['원숭이', '닭', '개', '돼지', '쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양']
        return zodiacs[year % 12] + '띠'

    def get_chinese_zodiac_lunar(self, lunar_date: date) -> str:
        """띠 계산 (음력 설날 기준 - 음력용)"""
        year = lunar_date.year
        zodiacs = ['원숭이', '닭', '개', '돼지', '쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양']
        return zodiacs[year % 12] + '띠'
