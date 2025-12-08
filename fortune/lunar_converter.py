"""
음력-양력 변환 유틸리티
"""
from datetime import date
from typing import Optional
from korean_lunar_calendar import KoreanLunarCalendar


def lunar_to_solar(lunar_date: date, is_leap_month: bool = False) -> Optional[date]:
    """
    음력 날짜를 양력 날짜로 변환

    Args:
        lunar_date: 음력 날짜 (date 객체)
        is_leap_month: 윤달 여부 (기본값: False)

    Returns:
        양력 날짜 (date 객체), 변환 실패 시 None
    """
    try:
        calendar = KoreanLunarCalendar()

        # 음력 설정
        calendar.setLunarDate(
            lunar_date.year,
            lunar_date.month,
            lunar_date.day,
            is_leap_month
        )

        # 양력으로 변환
        solar_year = calendar.solarYear
        solar_month = calendar.solarMonth
        solar_day = calendar.solarDay

        return date(solar_year, solar_month, solar_day)

    except Exception as e:
        print(f"[ERROR] 음력->양력 변환 실패: {e}")
        return None


def solar_to_lunar(solar_date: date) -> Optional[dict]:
    """
    양력 날짜를 음력 날짜로 변환

    Args:
        solar_date: 양력 날짜 (date 객체)

    Returns:
        음력 정보 딕셔너리 {'year', 'month', 'day', 'is_leap_month'}
        변환 실패 시 None
    """
    try:
        calendar = KoreanLunarCalendar()

        # 양력 설정
        calendar.setSolarDate(
            solar_date.year,
            solar_date.month,
            solar_date.day
        )

        return {
            'year': calendar.lunarYear,
            'month': calendar.lunarMonth,
            'day': calendar.lunarDay,
            'is_leap_month': calendar.isLunarLeapMonth
        }

    except Exception as e:
        print(f"[ERROR] 양력->음력 변환 실패: {e}")
        return None
