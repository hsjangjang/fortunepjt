"""
행운 아이템 결정 서비스
"""
from datetime import date
from typing import Dict, List, Optional

from ..constants import (
    FORTUNE_NAMES, COMBO_TO_INDEX,
    HIGH_SCORE_ITEMS, MID_SCORE_ITEMS, LOW_SCORE_ITEMS,
    ZODIAC_ITEMS, DEFAULT_ZODIAC_ITEM
)


class ItemService:
    """행운 아이템 결정 서비스"""

    def determine_lucky_item(
        self,
        zodiac_sign: str,
        today: date,
        user_id: int = None,
        session_key: str = None,
        lucky_colors: List[str] = None,
        fortune_score: int = 70,
        fortune_scores: Dict = None
    ) -> Dict:
        """행운의 아이템 결정 - 점수대별 6개 아이템, 낮은 운 2개 조합(4C2=6)으로 선택"""
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
        lowest_two = tuple(sorted([sorted_scores[0][0], sorted_scores[1][0]]))

        # 낮은 운 2개 조합으로 아이템 인덱스 결정
        item_idx = COMBO_TO_INDEX.get(lowest_two, 0)

        # 총점 기반 아이템 풀 선택
        if fortune_score >= 80:
            item_pool = HIGH_SCORE_ITEMS
        elif fortune_score >= 60:
            item_pool = MID_SCORE_ITEMS
        else:
            item_pool = LOW_SCORE_ITEMS

        selected_item = item_pool[item_idx]

        # 설명 생성
        lowest_fortune_name = FORTUNE_NAMES[sorted_scores[0][0]]
        second_fortune_name = FORTUNE_NAMES[sorted_scores[1][0]]
        main_description = selected_item[4]

        # 별자리 아이템 선택 (날짜별 순환)
        zodiac_item_list = ZODIAC_ITEMS.get(zodiac_sign, [DEFAULT_ZODIAC_ITEM])
        zodiac_item_idx = (today.day - 1) % len(zodiac_item_list)
        zodiac_item = zodiac_item_list[zodiac_item_idx]
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
