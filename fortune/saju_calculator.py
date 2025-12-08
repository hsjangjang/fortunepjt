"""
정확한 사주 만세력 계산 모듈
- 년주, 월주, 일주, 시주 계산
- 천간/지지의 오행 점수 계산
- 지장간(숨은 천간) 포함 계산
"""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

class SajuCalculator:
    """정확한 사주팔자 및 오행 계산 클래스"""
    
    # 천간 (10개)
    CHEONGAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
    CHEONGAN_HANJA = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 지지 (12개)
    JIJI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
    JIJI_HANJA = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 천간의 오행
    CHEONGAN_OHAENG = {
        '갑': '목', '을': '목',
        '병': '화', '정': '화',
        '무': '토', '기': '토',
        '경': '금', '신': '금',
        '임': '수', '계': '수'
    }
    
    # 지지의 오행
    JIJI_OHAENG = {
        '자': '수', '축': '토', '인': '목', '묘': '목',
        '진': '토', '사': '화', '오': '화', '미': '토',
        '신': '금', '유': '금', '술': '토', '해': '수'
    }
    
    # 지장간 (지지 안에 숨어있는 천간들과 그 비율)
    # 형식: {지지: [(천간, 비율), ...]}
    JIJANGGAN = {
        '자': [('계', 100)],
        '축': [('계', 30), ('신', 3), ('기', 67)],
        '인': [('무', 7), ('병', 7), ('갑', 86)],
        '묘': [('을', 100)],
        '진': [('을', 30), ('계', 3), ('무', 67)],
        '사': [('무', 7), ('경', 7), ('병', 86)],
        '오': [('기', 30), ('정', 70)],
        '미': [('정', 30), ('을', 3), ('기', 67)],
        '신': [('무', 7), ('임', 7), ('경', 86)],
        '유': [('신', 100)],
        '술': [('신', 30), ('정', 3), ('무', 67)],
        '해': [('무', 7), ('갑', 7), ('임', 86)]
    }
    
    # 천간의 음양
    CHEONGAN_EUMYANG = {
        '갑': '양', '을': '음',
        '병': '양', '정': '음',
        '무': '양', '기': '음',
        '경': '양', '신': '음',
        '임': '양', '계': '음'
    }
    
    # 지지의 음양
    JIJI_EUMYANG = {
        '자': '양', '축': '음', '인': '양', '묘': '음',
        '진': '양', '사': '음', '오': '양', '미': '음',
        '신': '양', '유': '음', '술': '양', '해': '음'
    }
    
    # 24절기 (절기와 중기)
    # 절기: 월의 시작을 나타냄 (입춘, 경칩, 청명, 입하, 망종, 소서, 입추, 백로, 한로, 입동, 대설, 소한)
    JEOLGI = [
        '소한', '대한', '입춘', '우수', '경칩', '춘분',
        '청명', '곡우', '입하', '소만', '망종', '하지',
        '소서', '대서', '입추', '처서', '백로', '추분',
        '한로', '상강', '입동', '소설', '대설', '동지'
    ]
    
    # 월건 (월주의 지지) - 인월(1월)부터 시작
    WOLJI = ['인', '묘', '진', '사', '오', '미', '신', '유', '술', '해', '자', '축']
    
    # 년간에 따른 월간 시작 천간 (년상기월법)
    # 갑/기년 -> 병인월, 을/경년 -> 무인월, 병/신년 -> 경인월, 정/임년 -> 임인월, 무/계년 -> 갑인월
    WOLGAN_START = {
        '갑': 2, '기': 2,  # 병(2)부터
        '을': 4, '경': 4,  # 무(4)부터
        '병': 6, '신': 6,  # 경(6)부터
        '정': 8, '임': 8,  # 임(8)부터
        '무': 0, '계': 0   # 갑(0)부터
    }
    
    # 일간에 따른 시간 시작 천간 (일상기시법)
    SIGAN_START = {
        '갑': 0, '기': 0,  # 갑자시
        '을': 2, '경': 2,  # 병자시
        '병': 4, '신': 4,  # 무자시
        '정': 6, '임': 6,  # 경자시
        '무': 8, '계': 8   # 임자시
    }
    
    # 기준일: 1900년 1월 31일은 갑진(甲辰)일
    BASE_DATE = date(1900, 1, 31)
    BASE_DAY_GANZI = (0, 4)  # 갑(0), 진(4)
    
    # 절기 데이터 (년도별 절기 시작일) - 일부 샘플, 실제로는 더 많은 데이터 필요
    # 형식: {년도: [(월, 일, 시, 분), ...]} - 24절기 순서대로
    
    def __init__(self):
        pass
    
    def calculate_saju(
        self, 
        birth_date: date, 
        birth_time: Optional[datetime] = None,
        use_jaси_split: bool = False  # 자시 분리 (야자시/조자시) 적용 여부
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
        # 년주 계산
        year_gan, year_ji = self._calculate_year_pillar(birth_date)
        
        # 월주 계산 (절기 기준)
        month_gan, month_ji = self._calculate_month_pillar(birth_date, year_gan)
        
        # 일주 계산
        day_gan, day_ji = self._calculate_day_pillar(birth_date)
        
        # 시주 계산
        if birth_time:
            hour_gan, hour_ji = self._calculate_hour_pillar(birth_time, day_gan, use_jaси_split)
        else:
            hour_gan, hour_ji = None, None
        
        # 사주 데이터 구성
        saju = {
            'year': {'gan': year_gan, 'ji': year_ji, 'ganzi': f"{year_gan}{year_ji}"},
            'month': {'gan': month_gan, 'ji': month_ji, 'ganzi': f"{month_gan}{month_ji}"},
            'day': {'gan': day_gan, 'ji': day_ji, 'ganzi': f"{day_gan}{day_ji}"},
            'hour': {'gan': hour_gan, 'ji': hour_ji, 'ganzi': f"{hour_gan}{hour_ji}" if hour_gan else "미상"}
        }
        
        # 오행 점수 계산
        ohaeng_scores = self._calculate_ohaeng_scores(saju)
        
        # 일간 오행 (본인의 오행)
        day_ohaeng = self.CHEONGAN_OHAENG[day_gan]
        
        # 가장 강한 오행
        strongest_ohaeng = max(ohaeng_scores.items(), key=lambda x: x[1])[0]
        
        # 일주 강약 계산
        ilju_strength = self._calculate_ilju_strength(saju, ohaeng_scores)
        
        return {
            'saju': saju,
            'ohaeng_scores': ohaeng_scores,
            'day_ohaeng': day_ohaeng,  # 일간 기준 오행
            'strongest_ohaeng': strongest_ohaeng,  # 가장 강한 오행
            'ilju_strength': ilju_strength,  # 신강/신약
            'year_hanja': f"{self.CHEONGAN_HANJA[self.CHEONGAN.index(year_gan)]}{self.JIJI_HANJA[self.JIJI.index(year_ji)]}",
            'month_hanja': f"{self.CHEONGAN_HANJA[self.CHEONGAN.index(month_gan)]}{self.JIJI_HANJA[self.JIJI.index(month_ji)]}",
            'day_hanja': f"{self.CHEONGAN_HANJA[self.CHEONGAN.index(day_gan)]}{self.JIJI_HANJA[self.JIJI.index(day_ji)]}",
            'hour_hanja': f"{self.CHEONGAN_HANJA[self.CHEONGAN.index(hour_gan)]}{self.JIJI_HANJA[self.JIJI.index(hour_ji)]}" if hour_gan else "미상"
        }
    
    def _calculate_year_pillar(self, birth_date: date) -> Tuple[str, str]:
        """
        년주 계산 (입춘 기준)
        - 입춘 전이면 전년도로 계산
        """
        year = birth_date.year
        
        # 입춘 날짜 계산 (대략 2월 4일)
        # 더 정확한 계산을 위해서는 절기 데이터베이스 필요
        ipchun = self._get_ipchun_date(year)
        
        if birth_date < ipchun:
            year -= 1
        
        # 년간 계산: (년도 - 4) % 10
        year_gan_idx = (year - 4) % 10
        # 년지 계산: (년도 - 4) % 12
        year_ji_idx = (year - 4) % 12
        
        return self.CHEONGAN[year_gan_idx], self.JIJI[year_ji_idx]
    
    def _get_ipchun_date(self, year: int) -> date:
        """
        입춘 날짜 계산 (근사값)
        실제로는 천문 계산이나 데이터베이스 필요
        """
        # 입춘은 대략 2월 3~5일 사이
        # 더 정확한 계산을 위한 근사 공식
        # 기준: 2000년 입춘 = 2월 4일 14:14
        
        base_year = 2000
        base_day = 4.0 + (14 * 60 + 14) / (24 * 60)  # 2000년 입춘
        
        # 1년에 약 5시간 46분씩 늦어짐 (0.2422일)
        # 4년마다 하루 빠름 (윤년 보정)
        
        diff_years = year - base_year
        day_offset = diff_years * 0.2422
        leap_correction = diff_years // 4
        
        adjusted_day = base_day + day_offset - leap_correction
        
        # 2월 기준
        if adjusted_day >= 28:
            adjusted_day -= 28
            month = 3
        else:
            month = 2
        
        return date(year, month, int(adjusted_day) + 1)
    
    def _calculate_month_pillar(self, birth_date: date, year_gan: str) -> Tuple[str, str]:
        """
        월주 계산 (절기 기준)
        """
        # 절기에 따른 월 계산
        solar_month = self._get_solar_month(birth_date)
        
        # 월지
        month_ji = self.WOLJI[solar_month - 1]
        
        # 월간 (년상기월법)
        start_idx = self.WOLGAN_START[year_gan]
        month_gan_idx = (start_idx + (solar_month - 1)) % 10
        month_gan = self.CHEONGAN[month_gan_idx]
        
        return month_gan, month_ji
    
    def _get_solar_month(self, birth_date: date) -> int:
        """
        절기 기준 월 계산 (1~12월)
        - 1월: 입춘 ~ 경칩 전
        - 2월: 경칩 ~ 청명 전
        - ...
        """
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day
        
        # 절기별 대략적인 시작일 (매년 약간씩 다름)
        # 형식: (월, 일) - 절기 시작
        jeolgi_dates = [
            (2, 4),   # 입춘 (1월 시작)
            (3, 6),   # 경칩 (2월 시작)
            (4, 5),   # 청명 (3월 시작)
            (5, 6),   # 입하 (4월 시작)
            (6, 6),   # 망종 (5월 시작)
            (7, 7),   # 소서 (6월 시작)
            (8, 8),   # 입추 (7월 시작)
            (9, 8),   # 백로 (8월 시작)
            (10, 8),  # 한로 (9월 시작)
            (11, 7),  # 입동 (10월 시작)
            (12, 7),  # 대설 (11월 시작)
            (1, 6),   # 소한 (12월 시작)
        ]
        
        # 현재 날짜가 어느 절기에 해당하는지 확인
        for i, (jeol_month, jeol_day) in enumerate(jeolgi_dates):
            # 다음 절기
            next_idx = (i + 1) % 12
            next_month, next_day = jeolgi_dates[next_idx]
            
            # 현재 절기 범위에 있는지 확인
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
        
        # 소한 이전 (전년 12월)
        if month == 1 and day < 6:
            return 12
        
        # 기본값 (절기 계산 실패 시)
        return ((month + 9) % 12) + 1
    
    def _calculate_day_pillar(self, birth_date: date) -> Tuple[str, str]:
        """
        일주 계산
        - 기준일로부터의 경과일 수로 계산
        """
        # 기준일로부터의 일수 차이
        diff = (birth_date - self.BASE_DATE).days
        
        # 일간
        day_gan_idx = (self.BASE_DAY_GANZI[0] + diff) % 10
        # 일지
        day_ji_idx = (self.BASE_DAY_GANZI[1] + diff) % 12
        
        return self.CHEONGAN[day_gan_idx], self.JIJI[day_ji_idx]
    
    def _calculate_hour_pillar(
        self, 
        birth_time: datetime, 
        day_gan: str,
        use_jasi_split: bool = False
    ) -> Tuple[str, str]:
        """
        시주 계산
        """
        hour = birth_time.hour
        
        # 시지 결정 (2시간 단위)
        # 자시: 23:00-01:00, 축시: 01:00-03:00, ...
        if hour == 23 or hour == 0:
            hour_ji_idx = 0  # 자
        else:
            hour_ji_idx = ((hour + 1) // 2) % 12
        
        hour_ji = self.JIJI[hour_ji_idx]
        
        # 시간 (일상기시법)
        start_idx = self.SIGAN_START[day_gan]
        hour_gan_idx = (start_idx + hour_ji_idx) % 10
        hour_gan = self.CHEONGAN[hour_gan_idx]
        
        return hour_gan, hour_ji
    
    def _calculate_ohaeng_scores(self, saju: Dict) -> Dict[str, int]:
        """
        오행 점수 계산 (천간 + 지지 + 지장간 포함)
        """
        scores = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
        
        # 각 기둥별 점수 가중치
        pillar_weights = {
            'year': 1.0,
            'month': 1.0,
            'day': 1.0,
            'hour': 1.0
        }
        
        for pillar_name, pillar in saju.items():
            if pillar['gan'] is None:
                continue
                
            weight = pillar_weights.get(pillar_name, 1.0)
            
            # 천간 오행 점수 (기본 10점)
            gan = pillar['gan']
            gan_ohaeng = self.CHEONGAN_OHAENG[gan]
            scores[gan_ohaeng] += int(10 * weight)
            
            # 지지 오행 점수 (기본 10점)
            ji = pillar['ji']
            ji_ohaeng = self.JIJI_OHAENG[ji]
            scores[ji_ohaeng] += int(10 * weight)
            
            # 지장간 오행 점수 (비율에 따라)
            if ji in self.JIJANGGAN:
                for jijang_gan, ratio in self.JIJANGGAN[ji]:
                    jijang_ohaeng = self.CHEONGAN_OHAENG[jijang_gan]
                    # 비율에 따른 점수 (최대 10점 기준)
                    scores[jijang_ohaeng] += int((ratio / 100) * 10 * weight)
        
        return scores
    
    def _calculate_ilju_strength(self, saju: Dict, ohaeng_scores: Dict) -> Dict:
        """
        일주 강약 계산 (신강/신약)
        """
        day_gan = saju['day']['gan']
        day_ohaeng = self.CHEONGAN_OHAENG[day_gan]
        
        # 나를 도와주는 오행 (비겁 + 인성)
        helping_ohaeng = self._get_helping_ohaeng(day_ohaeng)
        
        # 나를 소모시키는 오행 (식상 + 재성 + 관성)
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
        ohaeng_cycle = ['목', '화', '토', '금', '수']
        my_idx = ohaeng_cycle.index(my_ohaeng)
        
        # 비겁: 같은 오행
        # 인성: 나를 생해주는 오행
        generating_idx = (my_idx - 1) % 5
        
        return [my_ohaeng, ohaeng_cycle[generating_idx]]
    
    def _get_draining_ohaeng(self, my_ohaeng: str) -> List[str]:
        """나를 소모시키는 오행 (식상 + 재성 + 관성)"""
        ohaeng_cycle = ['목', '화', '토', '금', '수']
        my_idx = ohaeng_cycle.index(my_ohaeng)
        
        # 식상: 내가 생해주는 오행
        # 재성: 내가 극하는 오행
        # 관성: 나를 극하는 오행
        generating_idx = (my_idx + 1) % 5  # 식상
        controlling_idx = (my_idx + 2) % 5  # 재성
        controlled_by_idx = (my_idx - 2) % 5  # 관성
        
        return [ohaeng_cycle[generating_idx], ohaeng_cycle[controlling_idx], ohaeng_cycle[controlled_by_idx]]
    
    def get_dominant_ohaeng(self, birth_date: date, birth_time: Optional[datetime] = None) -> str:
        """
        가장 강한 오행 반환 (간단한 인터페이스)
        """
        result = self.calculate_saju(birth_date, birth_time)
        return result['strongest_ohaeng']
    
    def get_day_ohaeng(self, birth_date: date) -> str:
        """
        일간 기준 오행 반환 (간단한 인터페이스)
        """
        result = self.calculate_saju(birth_date)
        return result['day_ohaeng']


# 테스트
if __name__ == "__main__":
    calc = SajuCalculator()
    
    # 테스트: 1998년 12월 19일
    test_date = date(1998, 12, 19)
    test_time = datetime(1998, 12, 19, 10, 30)  # 오전 10:30 (사시)
    
    result = calc.calculate_saju(test_date, test_time)
    
    print("=" * 50)
    print(f"생년월일: {test_date}")
    print(f"태어난 시간: {test_time.strftime('%H:%M')}")
    print("=" * 50)
    print("\n[사주팔자]")
    print(f"년주: {result['saju']['year']['ganzi']} ({result['year_hanja']})")
    print(f"월주: {result['saju']['month']['ganzi']} ({result['month_hanja']})")
    print(f"일주: {result['saju']['day']['ganzi']} ({result['day_hanja']})")
    print(f"시주: {result['saju']['hour']['ganzi']} ({result['hour_hanja']})")
    
    print("\n[오행 점수]")
    for ohaeng, score in result['ohaeng_scores'].items():
        print(f"  {ohaeng}: {score}")
    
    print(f"\n[일간 오행]: {result['day_ohaeng']}")
    print(f"[가장 강한 오행]: {result['strongest_ohaeng']}")
    print(f"[일주 강약]: {result['ilju_strength']['strength']} ({result['ilju_strength']['ratio']})")
