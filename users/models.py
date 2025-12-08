from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    """커스텀 User 모델"""
    
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]
    
    MBTI_CHOICES = [
        ('INTJ', 'INTJ'), ('INTP', 'INTP'), ('ENTJ', 'ENTJ'), ('ENTP', 'ENTP'),
        ('INFJ', 'INFJ'), ('INFP', 'INFP'), ('ENFJ', 'ENFJ'), ('ENFP', 'ENFP'),
        ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP'),
    ]
    
    PERSONAL_COLOR_CHOICES = [
        ('spring_warm', '봄 웜톤'),
        ('summer_cool', '여름 쿨톤'),
        ('autumn_warm', '가을 웜톤'),
        ('winter_cool', '겨울 쿨톤'),
    ]

    CALENDAR_TYPE_CHOICES = [
        ('solar', '양력'),
        ('lunar', '음력'),
    ]

    # 필수 정보
    birth_date = models.DateField(verbose_name='생년월일', null=True)
    calendar_type = models.CharField(
        max_length=10,
        choices=CALENDAR_TYPE_CHOICES,
        default='solar',
        verbose_name='양력/음력'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name='성별',
        blank=True
    )
    
    # 선택 정보
    birth_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='태어난 시각'
    )
    chinese_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='한자 이름'
    )
    mbti = models.CharField(
        max_length=4,
        choices=MBTI_CHOICES,
        blank=True,
        verbose_name='MBTI'
    )
    personal_color = models.CharField(
        max_length=20,
        choices=PERSONAL_COLOR_CHOICES,
        blank=True,
        verbose_name='퍼스널컬러'
    )
    
    # 추가 정보
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='전화번호'
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        verbose_name='프로필 이미지'
    )
    
    # 임시 비밀번호 플래그
    must_change_password = models.BooleanField(
        default=False,
        verbose_name='비밀번호 변경 필요'
    )

    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
    
    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"
    
    @property
    def age(self):
        """나이 계산"""
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    @property
    def zodiac_sign(self):
        """별자리 계산"""
        if not self.birth_date:
            return None
        month = self.birth_date.month
        day = self.birth_date.day
        
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
    
    @property
    def chinese_zodiac(self):
        """띠 계산"""
        if not self.birth_date:
            return None
        zodiacs = ['원숭이', '닭', '개', '돼지', '쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양']
        return zodiacs[self.birth_date.year % 12] + '띠'

    @property
    def birth_time_display(self):
        """태어난 시간 포맷팅 (오전/오후 HH:MM)"""
        if not self.birth_time:
            return None
        hour = self.birth_time.hour
        minute = self.birth_time.strftime('%M')
        period = '오전' if hour < 12 else '오후'
        display_hour = 12 if hour == 0 else (hour - 12 if hour > 12 else hour)
        return f"{period} {display_hour:02d}:{minute}"
