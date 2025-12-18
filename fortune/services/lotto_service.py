"""
로또 번호 생성 서비스
"""
import hashlib
from datetime import date
from typing import Dict, List, Optional


class LottoService:
    """로또 번호 생성 서비스"""

    def generate_lucky_numbers(
        self,
        birth_date: date,
        today: date,
        fortune_scores: Dict = None,
        gender: str = None,
        user_id: int = None,
        session_key: str = None
    ) -> List[int]:
        """개인별 행운의 로또 번호 생성 (user_id 또는 session_key 기반)"""
        gender_num = 1 if gender == 'M' else 2 if gender == 'F' else 0

        # 사용자 식별자 결정
        if user_id:
            user_identifier = f"user_{user_id}"
        elif session_key:
            user_identifier = f"session_{session_key}"
        else:
            import uuid
            user_identifier = f"random_{uuid.uuid4()}"

        # 시드 생성
        birth_num = birth_date.year * 10000 + birth_date.month * 100 + birth_date.day
        base_seed = f"lotto_{user_identifier}_{today.isoformat()}_{birth_num}_{gender_num}"

        # 해시 기반으로 6개 고유 번호 선택
        selected = []
        attempt = 0
        while len(selected) < 6 and attempt < 100:
            seed_string = f"{base_seed}_num{attempt}"
            hash_value = int(hashlib.sha256(seed_string.encode()).hexdigest(), 16)
            num = (hash_value % 45) + 1

            if num not in selected:
                selected.append(num)
            attempt += 1

        return sorted(selected)
