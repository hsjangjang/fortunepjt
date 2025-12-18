"""
행운색 결정 서비스
"""
import hashlib
from datetime import date
from typing import Dict, List, Optional

from ..constants import (
    STAR_SIGN_COLORS, CHINESE_ZODIAC_COLORS, ALL_COLORS,
    PERSONAL_COLOR_PALETTES, PERSONAL_COLOR_AVOID
)


class ColorService:
    """행운색 결정 서비스"""

    def determine_lucky_colors(
        self,
        zodiac_sign: str,
        chinese_zodiac: str,
        today: date,
        fortune_scores: Dict = None,
        personal_color: Optional[str] = None
    ) -> List[str]:
        """행운의 색상들 결정 (별자리 + 띠 + 날짜 + 운세점수 + 퍼스널컬러 기반)"""
        seed_string = f"{zodiac_sign}_{chinese_zodiac}_{today.isoformat()}_{personal_color or 'none'}"
        seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)

        # 별자리/띠 색상 풀
        star_colors = STAR_SIGN_COLORS.get(zodiac_sign, ALL_COLORS[:5])
        zodiac_colors = CHINESE_ZODIAC_COLORS.get(chinese_zodiac, [])
        candidate_colors = list(star_colors) + list(zodiac_colors)

        # 퍼스널컬러 우선 적용
        avoid_colors = []
        if personal_color and personal_color in PERSONAL_COLOR_PALETTES:
            personal_palette = PERSONAL_COLOR_PALETTES[personal_color]
            candidate_colors = list(personal_palette) + candidate_colors
            avoid_colors = PERSONAL_COLOR_AVOID.get(personal_color, [])

        # 운세 점수에 따른 색상 추가
        if fortune_scores:
            total_score = fortune_scores.get('total', 50)
            if total_score >= 80:
                candidate_colors.extend(['금색', '노란색', '흰색'])
            elif total_score >= 60:
                candidate_colors.extend(['하늘색', '분홍색'])
            elif total_score < 40:
                candidate_colors.extend(['남색', '회색', '베이지색'])

        # 피해야 할 색상 제거
        if avoid_colors:
            candidate_colors = [c for c in candidate_colors if c not in avoid_colors]

        # 중복 제거
        candidate_colors = list(dict.fromkeys(candidate_colors))

        # 시드 기반 3개 선택
        selected_colors = []
        for i in range(3):
            if not candidate_colors:
                break
            idx = (seed_hash + i * 7) % len(candidate_colors)
            selected_colors.append(candidate_colors[idx])
            candidate_colors.pop(idx)

        # 3개 미만이면 보충
        if len(selected_colors) < 3:
            remaining = [c for c in ALL_COLORS if c not in selected_colors and c not in avoid_colors]
            for i in range(3 - len(selected_colors)):
                if remaining:
                    idx = (seed_hash + i * 13) % len(remaining)
                    selected_colors.append(remaining[idx])
                    remaining.pop(idx)

        return selected_colors if selected_colors else ['파란색', '초록색', '노란색']
