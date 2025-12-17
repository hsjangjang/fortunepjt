"""
정확한 사주 만세력 계산 모듈
- 년주, 월주, 일주, 시주 계산
- 천간/지지의 오행 점수 계산
- 지장간(숨은 천간) 포함 계산
"""
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from .saju_data import (
    CHEONGAN, CHEONGAN_HANJA, JIJI, JIJI_HANJA,
    CHEONGAN_OHAENG, JIJI_OHAENG, JIJANGGAN,
    WOLJI, WOLGAN_START, SIGAN_START,
    BASE_DATE, BASE_DAY_GANZI, JEOLGI_DATES, OHAENG_CYCLE
)


class SajuCalculator:
    """정확한 사주팔자 및 오행 계산 클래스"""

    def __init__(self):
        pass

    def calculate_saju(
        self,
        birth_date: date,
        birth_time: Optional[datetime] = None,
        use_jasi_split: bool = False
    ) -> Dict:
        """
        사주팔자 계산 메인 함수

        Args:
            birth_date: 생년월일
            birth_time: 태어난 시간 (없으면 시주는 미상으로 처리)
            use_jasi_split: 자시 분리 적용 여부

        Returns:
            사주팔자 정보 딕셔너리
        """
        year_gan, year_ji = self._calculate_year_pillar(birth_date)
        month_gan, month_ji = self._calculate_month_pillar(birth_date, year_gan)
        day_gan, day_ji = self._calculate_day_pillar(birth_date)

        if birth_time:
            hour_gan, hour_ji = self._calculate_hour_pillar(birth_time, day_gan)
        else:
            hour_gan, hour_ji = None, None

        saju = {
            'year': {'gan': year_gan, 'ji': year_ji, 'ganzi': f"{year_gan}{year_ji}"},
            'month': {'gan': month_gan, 'ji': month_ji, 'ganzi': f"{month_gan}{month_ji}"},
            'day': {'gan': day_gan, 'ji': day_ji, 'ganzi': f"{day_gan}{day_ji}"},
            'hour': {'gan': hour_gan, 'ji': hour_ji, 'ganzi': f"{hour_gan}{hour_ji}" if hour_gan else "미상"}
        }

        ohaeng_scores = self._calculate_ohaeng_scores(saju)
        day_ohaeng = CHEONGAN_OHAENG[day_gan]
        strongest_ohaeng = max(ohaeng_scores.items(), key=lambda x: x[1])[0]
        ilju_strength = self._calculate_ilju_strength(saju, ohaeng_scores)

        return {
            'saju': saju,
            'ohaeng_scores': ohaeng_scores,
            'day_ohaeng': day_ohaeng,
            'strongest_ohaeng': strongest_ohaeng,
            'ilju_strength': ilju_strength,
            'year_hanja': f"{CHEONGAN_HANJA[CHEONGAN.index(year_gan)]}{JIJI_HANJA[JIJI.index(year_ji)]}",
            'month_hanja': f"{CHEONGAN_HANJA[CHEONGAN.index(month_gan)]}{JIJI_HANJA[JIJI.index(month_ji)]}",
            'day_hanja': f"{CHEONGAN_HANJA[CHEONGAN.index(day_gan)]}{JIJI_HANJA[JIJI.index(day_ji)]}",
            'hour_hanja': f"{CHEONGAN_HANJA[CHEONGAN.index(hour_gan)]}{JIJI_HANJA[JIJI.index(hour_ji)]}" if hour_gan else "미상"
        }

    def _calculate_year_pillar(self, birth_date: date) -> Tuple[str, str]:
        """년주 계산 (입춘 기준)"""
        year = birth_date.year
        ipchun = self._get_ipchun_date(year)

        if birth_date < ipchun:
            year -= 1

        year_gan_idx = (year - 4) % 10
        year_ji_idx = (year - 4) % 12

        return CHEONGAN[year_gan_idx], JIJI[year_ji_idx]

    def _get_ipchun_date(self, year: int) -> date:
        """입춘 날짜 계산 (근사값)"""
        base_year = 2000
        base_day = 4.0 + (14 * 60 + 14) / (24 * 60)

        diff_years = year - base_year
        day_offset = diff_years * 0.2422
        leap_correction = diff_years // 4

        adjusted_day = base_day + day_offset - leap_correction

        if adjusted_day >= 28:
            adjusted_day -= 28
            month = 3
        else:
            month = 2

        return date(year, month, int(adjusted_day) + 1)

    def _calculate_month_pillar(self, birth_date: date, year_gan: str) -> Tuple[str, str]:
        """월주 계산 (절기 기준)"""
        solar_month = self._get_solar_month(birth_date)
        month_ji = WOLJI[solar_month - 1]

        start_idx = WOLGAN_START[year_gan]
        month_gan_idx = (start_idx + (solar_month - 1)) % 10
        month_gan = CHEONGAN[month_gan_idx]

        return month_gan, month_ji

    def _get_solar_month(self, birth_date: date) -> int:
        """절기 기준 월 계산 (1~12월)"""
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day

        for i, (jeol_month, jeol_day) in enumerate(JEOLGI_DATES):
            next_idx = (i + 1) % 12
            next_month, next_day = JEOLGI_DATES[next_idx]

            current_jeolgi_date = date(year if jeol_month <= 12 else year, jeol_month, jeol_day)

            if jeol_month == 12 and next_month == 1:
                next_jeolgi_date = date(year + 1, next_month, next_day)
            elif jeol_month == 1 and month >= 1:
                current_jeolgi_date = date(year, jeol_month, jeol_day)
                next_jeolgi_date = date(year, next_month, next_day)
            else:
                next_jeolgi_date = date(year, next_month, next_day)

            if current_jeolgi_date <= birth_date < next_jeolgi_date:
                return (i % 12) + 1

        if month == 1 and day < 6:
            return 12

        return ((month + 9) % 12) + 1

    def _calculate_day_pillar(self, birth_date: date) -> Tuple[str, str]:
        """일주 계산"""
        diff = (birth_date - BASE_DATE).days
        day_gan_idx = (BASE_DAY_GANZI[0] + diff) % 10
        day_ji_idx = (BASE_DAY_GANZI[1] + diff) % 12

        return CHEONGAN[day_gan_idx], JIJI[day_ji_idx]

    def _calculate_hour_pillar(self, birth_time: datetime, day_gan: str) -> Tuple[str, str]:
        """시주 계산"""
        hour = birth_time.hour

        if hour == 23 or hour == 0:
            hour_ji_idx = 0
        else:
            hour_ji_idx = ((hour + 1) // 2) % 12

        hour_ji = JIJI[hour_ji_idx]

        start_idx = SIGAN_START[day_gan]
        hour_gan_idx = (start_idx + hour_ji_idx) % 10
        hour_gan = CHEONGAN[hour_gan_idx]

        return hour_gan, hour_ji

    def _calculate_ohaeng_scores(self, saju: Dict) -> Dict[str, int]:
        """오행 점수 계산 (천간 + 지지 + 지장간 포함)"""
        scores = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
        pillar_weights = {'year': 1.0, 'month': 1.0, 'day': 1.0, 'hour': 1.0}

        for pillar_name, pillar in saju.items():
            if pillar['gan'] is None:
                continue

            weight = pillar_weights.get(pillar_name, 1.0)

            gan = pillar['gan']
            gan_ohaeng = CHEONGAN_OHAENG[gan]
            scores[gan_ohaeng] += int(10 * weight)

            ji = pillar['ji']
            ji_ohaeng = JIJI_OHAENG[ji]
            scores[ji_ohaeng] += int(10 * weight)

            if ji in JIJANGGAN:
                for jijang_gan, ratio in JIJANGGAN[ji]:
                    jijang_ohaeng = CHEONGAN_OHAENG[jijang_gan]
                    scores[jijang_ohaeng] += int((ratio / 100) * 10 * weight)

        return scores

    def _calculate_ilju_strength(self, saju: Dict, ohaeng_scores: Dict) -> Dict:
        """일주 강약 계산 (신강/신약)"""
        day_gan = saju['day']['gan']
        day_ohaeng = CHEONGAN_OHAENG[day_gan]

        helping_ohaeng = self._get_helping_ohaeng(day_ohaeng)
        draining_ohaeng = self._get_draining_ohaeng(day_ohaeng)

        helping_score = sum(ohaeng_scores[oh] for oh in helping_ohaeng)
        draining_score = sum(ohaeng_scores[oh] for oh in draining_ohaeng)
        total = helping_score + draining_score

        return {
            'helping': helping_score,
            'draining': draining_score,
            'total': total,
            'strength': '신강' if helping_score >= draining_score else '신약',
            'ratio': f"{helping_score}:{draining_score}"
        }

    def _get_helping_ohaeng(self, my_ohaeng: str) -> List[str]:
        """나를 도와주는 오행 (비겁 + 인성)"""
        my_idx = OHAENG_CYCLE.index(my_ohaeng)
        generating_idx = (my_idx - 1) % 5
        return [my_ohaeng, OHAENG_CYCLE[generating_idx]]

    def _get_draining_ohaeng(self, my_ohaeng: str) -> List[str]:
        """나를 소모시키는 오행 (식상 + 재성 + 관성)"""
        my_idx = OHAENG_CYCLE.index(my_ohaeng)
        generating_idx = (my_idx + 1) % 5
        controlling_idx = (my_idx + 2) % 5
        controlled_by_idx = (my_idx - 2) % 5
        return [OHAENG_CYCLE[generating_idx], OHAENG_CYCLE[controlling_idx], OHAENG_CYCLE[controlled_by_idx]]

    def get_dominant_ohaeng(self, birth_date: date, birth_time: Optional[datetime] = None) -> str:
        """가장 강한 오행 반환"""
        result = self.calculate_saju(birth_date, birth_time)
        return result['strongest_ohaeng']

    def get_day_ohaeng(self, birth_date: date) -> str:
        """일간 기준 오행 반환"""
        result = self.calculate_saju(birth_date)
        return result['day_ohaeng']
