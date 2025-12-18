"""
운세 점수 계산 서비스
"""
import random
from datetime import date
from typing import Dict


class ScoreService:
    """운세 점수 계산 서비스"""

    # 점수 범위 상수
    MIN_SCORE = 50
    MAX_SCORE = 100
    BASE_MIN = 55
    BASE_MAX = 90

    def calculate_all_fortunes(self, birth_date: date, today: date, saju_data: Dict = None) -> Dict:
        """각 운별 점수 계산 (사주 오행 기반, 최소 50점)"""
        base = random.randint(self.BASE_MIN, self.BASE_MAX)

        ohaeng_bonus = {'money': 0, 'love': 0, 'study': 0, 'work': 0}

        if saju_data and 'ohaeng_scores' in saju_data:
            ohaeng = saju_data['ohaeng_scores']
            total_ohaeng = sum(ohaeng.values()) if ohaeng else 1
            avg_ohaeng = total_ohaeng / 5 if total_ohaeng > 0 else 10

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
                for key in ohaeng_bonus:
                    ohaeng_bonus[key] += stability_bonus

            # 일주 강약 반영
            if saju_data.get('ilju_strength'):
                strength = saju_data['ilju_strength']
                if strength == '강':
                    base += 5
                elif strength == '약':
                    base -= 3

        # 오행 보너스 적용 (범위 제한: -15 ~ +15)
        ohaeng_bonus = {k: max(-15, min(15, v)) for k, v in ohaeng_bonus.items()}

        money = self._clamp_score(base + random.randint(-10, 15) + ohaeng_bonus['money'])
        love = self._clamp_score(base + random.randint(-15, 20) + ohaeng_bonus['love'])
        study = self._clamp_score(base + random.randint(-10, 10) + ohaeng_bonus['study'])
        work = self._clamp_score(base + random.randint(-10, 15) + ohaeng_bonus['work'])
        health = self._clamp_score(base + random.randint(-10, 10))

        total = round((money + love + study + work + health) / 5)

        return {
            'total': total,
            'money': money,
            'love': love,
            'study': study,
            'work': work,
            'health': health,
        }

    def _clamp_score(self, score: int) -> int:
        """점수를 MIN_SCORE ~ MAX_SCORE 범위로 제한"""
        return max(self.MIN_SCORE, min(self.MAX_SCORE, score))

    def get_tone_for_score(self, score: int) -> str:
        """점수에 따른 톤 가이드 반환"""
        if score >= 85:
            return "매우 긍정적이고 희망적인 톤. 성공과 행운을 강조"
        elif score >= 70:
            return "긍정적인 톤. 좋은 기회와 발전 가능성을 언급"
        elif score >= 55:
            return "보통 톤. 평온하고 무난한 하루, 큰 변화 없음을 언급"
        elif score >= 40:
            return "다소 주의가 필요한 톤. 신중함과 조심스러운 접근 권장"
        else:
            return "조심스러운 톤. 어려움이 있을 수 있으나 극복 가능함을 언급"

    def build_score_tone_guide(self, scores: Dict) -> str:
        """LLM 프롬프트용 점수 정보 및 톤 가이드 생성"""
        guide = "[점수별 작성 톤 가이드 - 반드시 점수에 맞는 톤으로 작성]\n"

        score_names = {
            'total': '총운',
            'money': '재물운',
            'love': '애정운',
            'study': '학업운',
            'work': '직장운',
            'health': '건강운'
        }

        for key, name in score_names.items():
            score = scores.get(key, 70)
            tone = self.get_tone_for_score(score)
            guide += f"- {name} ({score}점): {tone}\n"

        return guide
