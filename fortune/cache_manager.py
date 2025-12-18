"""
운세 캐시 관리자 - 일간/주간/월간 운세 캐시 통합 관리
"""
import json
from datetime import date
from typing import Optional, Dict, Any

from .models import DailyFortuneCache, WeeklyFortuneCache, MonthlyFortuneCache


class FortuneCacheManager:
    """운세 캐시 관리 클래스"""

    # 기간 타입 상수
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'

    @staticmethod
    def get_current_week():
        """현재 년도와 주차 반환 (ISO 주차 기준)"""
        today = date.today()
        iso_calendar = today.isocalendar()
        return iso_calendar[0], iso_calendar[1]

    @staticmethod
    def get_current_month():
        """현재 년도와 월 반환"""
        today = date.today()
        return today.year, today.month

    @classmethod
    def _get_cache_model(cls, period_type: str):
        """기간 타입에 따른 캐시 모델 반환"""
        models = {
            cls.DAILY: DailyFortuneCache,
            cls.WEEKLY: WeeklyFortuneCache,
            cls.MONTHLY: MonthlyFortuneCache
        }
        return models.get(period_type)

    @classmethod
    def _get_period_field(cls, period_type: str) -> str:
        """기간 타입에 따른 필터 필드명 반환"""
        fields = {
            cls.DAILY: 'fortune_date',
            cls.WEEKLY: 'week_number',
            cls.MONTHLY: 'month'
        }
        return fields.get(period_type, 'fortune_date')

    @classmethod
    def _get_label(cls, period_type: str) -> str:
        """기간 타입에 따른 로그 라벨 반환"""
        labels = {
            cls.DAILY: 'Daily',
            cls.WEEKLY: 'Weekly',
            cls.MONTHLY: 'Monthly'
        }
        return labels.get(period_type, 'Unknown')

    # ============================================================
    # 일간 캐시 관리
    # ============================================================

    @classmethod
    def save_daily_fortune(cls, user, session_key: str, fortune_date: date, fortune_data: Dict,
                           birth_date: date = None, birth_time: str = '',
                           calendar_type: str = 'solar', chinese_name: str = '') -> bool:
        """일간 운세 저장"""
        try:
            if user and user.is_authenticated:
                DailyFortuneCache.objects.filter(user=user, fortune_date=fortune_date).delete()
                if session_key:
                    DailyFortuneCache.objects.filter(session_key=session_key, fortune_date=fortune_date).delete()
            elif session_key:
                DailyFortuneCache.objects.filter(session_key=session_key, fortune_date=fortune_date).delete()
            else:
                return False

            cache = DailyFortuneCache(
                user=user if user and user.is_authenticated else None,
                session_key=session_key or '',
                fortune_date=fortune_date,
                fortune_score=fortune_data.get('fortune_score', 70),
                lucky_color=fortune_data.get('lucky_color', ''),
                full_fortune_data=json.dumps(fortune_data, ensure_ascii=False),
                birth_date=birth_date,
                birth_time=birth_time,
                calendar_type=calendar_type,
                chinese_name=chinese_name
            )
            cache.save()
            print(f"[Daily Cache] 저장 완료: user={user}, date={fortune_date}")
            return True
        except Exception as e:
            print(f"[Daily Cache] 저장 실패: {e}")
            return False

    @classmethod
    def load_daily_fortune(cls, user, session_key: str, fortune_date: date) -> Optional[Dict]:
        """일간 운세 로드"""
        try:
            cache = None
            if user and user.is_authenticated:
                cache = DailyFortuneCache.objects.filter(user=user, fortune_date=fortune_date).first()
            elif session_key:
                cache = DailyFortuneCache.objects.filter(session_key=session_key, fortune_date=fortune_date).first()

            if cache and cache.full_fortune_data:
                fortune_data = json.loads(cache.full_fortune_data)
                print(f"[Daily Cache] 히트: user={user}, date={fortune_date}")
                return fortune_data
            return None
        except Exception as e:
            print(f"[Daily Cache] 로드 실패: {e}")
            return None

    @classmethod
    def find_same_condition_daily(cls, fortune_date: date, birth_date: date,
                                  birth_time: str = '', calendar_type: str = 'solar',
                                  chinese_name: str = '') -> Optional[Dict]:
        """동일 조건 일간 캐시 찾기"""
        try:
            cache = DailyFortuneCache.objects.filter(
                fortune_date=fortune_date,
                birth_date=birth_date,
                birth_time=birth_time or '',
                calendar_type=calendar_type,
                chinese_name=chinese_name or ''
            ).order_by('created_at').first()

            if cache and cache.full_fortune_data:
                fortune_data = json.loads(cache.full_fortune_data)
                print(f"[Daily Cache] 동일 조건 캐시 히트: birth={birth_date}, date={fortune_date}")
                return fortune_data
            return None
        except Exception as e:
            print(f"[Daily Cache] 동일 조건 조회 실패: {e}")
            return None

    # ============================================================
    # 주간/월간 캐시 관리 (일반화)
    # ============================================================

    @classmethod
    def save_period_fortune(cls, period_type: str, user, session_key: str,
                            year: int, period_value: int, fortune_data: Dict,
                            birth_date: date = None, gender: str = '') -> bool:
        """주간/월간 운세 저장"""
        try:
            CacheModel = cls._get_cache_model(period_type)
            period_field = cls._get_period_field(period_type)
            label = cls._get_label(period_type)

            filter_kwargs = {'year': year, period_field: period_value}

            if user and user.is_authenticated:
                CacheModel.objects.filter(user=user, **filter_kwargs).delete()
                cache = CacheModel(user=user, session_key=session_key or '', **filter_kwargs)
            elif session_key:
                CacheModel.objects.filter(session_key=session_key, **filter_kwargs).delete()
                cache = CacheModel(session_key=session_key, **filter_kwargs)
            else:
                return False

            cache.birth_date = birth_date
            cache.gender = gender or ''
            cache.full_fortune_data = json.dumps(fortune_data, ensure_ascii=False)
            cache.save()
            print(f"[{label} Cache] 저장 완료: user={user}, year={year}, {period_field}={period_value}")
            return True
        except Exception as e:
            label = cls._get_label(period_type)
            print(f"[{label} Cache] 저장 실패: {e}")
            return False

    @classmethod
    def load_period_fortune(cls, period_type: str, user, session_key: str,
                            year: int, period_value: int) -> Optional[Dict]:
        """주간/월간 운세 로드"""
        try:
            CacheModel = cls._get_cache_model(period_type)
            period_field = cls._get_period_field(period_type)
            label = cls._get_label(period_type)

            filter_kwargs = {'year': year, period_field: period_value}

            if user and user.is_authenticated:
                cache = CacheModel.objects.filter(user=user, **filter_kwargs).first()
            elif session_key:
                cache = CacheModel.objects.filter(session_key=session_key, **filter_kwargs).first()
            else:
                return None

            if cache and cache.full_fortune_data:
                fortune_data = json.loads(cache.full_fortune_data)
                print(f"[{label} Cache] 히트: user={user}, year={year}, {period_field}={period_value}")
                return fortune_data
            return None
        except Exception as e:
            label = cls._get_label(period_type)
            print(f"[{label} Cache] 로드 실패: {e}")
            return None

    @classmethod
    def find_same_condition_period(cls, period_type: str, year: int, period_value: int,
                                   birth_date: date, gender: str = '') -> Optional[Dict]:
        """동일 조건 주간/월간 캐시 찾기"""
        try:
            CacheModel = cls._get_cache_model(period_type)
            period_field = cls._get_period_field(period_type)
            label = cls._get_label(period_type)

            print(f"[{label} Cache] 동일 조건 검색: birth={birth_date}, gender={gender}, year={year}")

            base_filter = {'year': year, period_field: period_value, 'birth_date': birth_date}

            # 1차: 정확히 일치
            cache = CacheModel.objects.filter(**base_filter, gender=gender or '').order_by('created_at').first()

            # 2차: gender가 비어있는 캐시 (마이그레이션 전 호환)
            if not cache and gender:
                cache = CacheModel.objects.filter(**base_filter, gender='').order_by('created_at').first()
                if cache:
                    print(f"[{label} Cache] 2차 검색(gender='') 히트")

            if cache and cache.full_fortune_data:
                fortune_data = json.loads(cache.full_fortune_data)
                print(f"[{label} Cache] 동일 조건 캐시 히트")
                return fortune_data

            print(f"[{label} Cache] 동일 조건 캐시 없음")
            return None
        except Exception as e:
            label = cls._get_label(period_type)
            print(f"[{label} Cache] 동일 조건 조회 실패: {e}")
            return None

    # ============================================================
    # 편의 메서드 (주간/월간)
    # ============================================================

    @classmethod
    def save_weekly_fortune(cls, user, session_key: str, year: int, week: int,
                            fortune_data: Dict, birth_date: date = None, gender: str = '') -> bool:
        return cls.save_period_fortune(cls.WEEKLY, user, session_key, year, week, fortune_data, birth_date, gender)

    @classmethod
    def save_monthly_fortune(cls, user, session_key: str, year: int, month: int,
                             fortune_data: Dict, birth_date: date = None, gender: str = '') -> bool:
        return cls.save_period_fortune(cls.MONTHLY, user, session_key, year, month, fortune_data, birth_date, gender)

    @classmethod
    def load_weekly_fortune(cls, user, session_key: str, year: int, week: int) -> Optional[Dict]:
        return cls.load_period_fortune(cls.WEEKLY, user, session_key, year, week)

    @classmethod
    def load_monthly_fortune(cls, user, session_key: str, year: int, month: int) -> Optional[Dict]:
        return cls.load_period_fortune(cls.MONTHLY, user, session_key, year, month)

    @classmethod
    def find_same_weekly(cls, year: int, week: int, birth_date: date, gender: str = '') -> Optional[Dict]:
        return cls.find_same_condition_period(cls.WEEKLY, year, week, birth_date, gender)

    @classmethod
    def find_same_monthly(cls, year: int, month: int, birth_date: date, gender: str = '') -> Optional[Dict]:
        return cls.find_same_condition_period(cls.MONTHLY, year, month, birth_date, gender)
