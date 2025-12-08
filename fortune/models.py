from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()


class DailyFortuneCache(models.Model):
    """일일 운세 캐시 - 하루 동안 고정된 운세 저장"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='사용자'
    )
    session_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='세션 키 (비회원용)'
    )
    fortune_date = models.DateField(
        verbose_name='운세 날짜',
        db_index=True
    )

    # 운세 계산 키 (동일 조건 캐시용)
    birth_date = models.DateField(
        verbose_name='생년월일',
        null=True,
        blank=True,
        db_index=True
    )
    birth_time = models.CharField(
        max_length=10,
        verbose_name='태어난 시간',
        blank=True,
        default=''
    )
    calendar_type = models.CharField(
        max_length=10,
        verbose_name='양력/음력',
        blank=True,
        default='solar'
    )
    chinese_name = models.CharField(
        max_length=100,
        verbose_name='한자 이름',
        blank=True,
        default=''
    )

    # 운세 정보
    fortune_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='운세 점수'
    )
    fortune_text = models.TextField(
        verbose_name='운세 내용'
    )
    
    # 행운 정보
    lucky_color = models.CharField(
        max_length=7,
        verbose_name='대표 행운색 (HEX)'
    )
    lucky_colors_json = models.TextField(
        verbose_name='행운색 목록 (JSON)',
        default='[]'
    )
    lucky_number = models.IntegerField(
        verbose_name='행운의 숫자',
        null=True,
        blank=True
    )
    lucky_direction = models.CharField(
        max_length=20,
        verbose_name='행운의 방향',
        blank=True
    )
    
    # 운세 요소
    zodiac_sign = models.CharField(
        max_length=20,
        verbose_name='별자리',
        blank=True
    )
    chinese_zodiac = models.CharField(
        max_length=20,
        verbose_name='띠',
        blank=True
    )
    
    # 사주 정보 (JSON)
    saju_data = models.TextField(
        verbose_name='사주 데이터 (JSON)',
        blank=True,
        default='{}'
    )

    # 전체 운세 데이터 (JSON) - 모든 필드를 통째로 저장
    full_fortune_data = models.TextField(
        verbose_name='전체 운세 데이터 (JSON)',
        blank=True,
        default='{}'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_fortune_cache'
        unique_together = [
            ['user', 'fortune_date'],
            ['session_key', 'fortune_date']
        ]
        verbose_name = '일일 운세 캐시'
        verbose_name_plural = '일일 운세 캐시'
        indexes = [
            models.Index(fields=['fortune_date', '-created_at']),
            models.Index(fields=['fortune_date', 'birth_date', 'birth_time', 'chinese_name']),
        ]
    
    def __str__(self):
        identifier = self.user.username if self.user else self.session_key
        return f"{identifier} - {self.fortune_date}"
    
    @property
    def lucky_colors(self):
        """JSON 문자열을 파이썬 객체로 변환"""
        try:
            return json.loads(self.lucky_colors_json)
        except:
            return []
    
    @lucky_colors.setter
    def lucky_colors(self, value):
        """파이썬 객체를 JSON 문자열로 저장"""
        self.lucky_colors_json = json.dumps(value, ensure_ascii=False)


class FortuneBaseData(models.Model):
    """운세 기본 데이터 (천간, 지지, 오행 등)"""
    
    CATEGORY_CHOICES = [
        ('heavenly_stem', '천간'),
        ('earthly_branch', '지지'),
        ('five_elements', '오행'),
        ('zodiac', '별자리'),
        ('chinese_zodiac', '띠'),
    ]
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='카테고리'
    )
    code = models.CharField(
        max_length=20,
        verbose_name='코드'
    )
    name_ko = models.CharField(
        max_length=50,
        verbose_name='한국어 이름'
    )
    name_cn = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='한자'
    )
    attributes = models.JSONField(
        default=dict,
        verbose_name='속성'
    )
    compatibility = models.JSONField(
        default=dict,
        verbose_name='상성/상극 정보'
    )
    
    class Meta:
        db_table = 'fortune_base_data'
        unique_together = ['category', 'code']
        verbose_name = '운세 기본 데이터'
        verbose_name_plural = '운세 기본 데이터'
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.name_ko}"


class ColorMaster(models.Model):
    """색상 마스터 데이터"""
    
    color_code = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='색상 코드 (HEX)'
    )
    color_name = models.CharField(
        max_length=50,
        verbose_name='색상 이름'
    )
    color_category = models.CharField(
        max_length=30,
        verbose_name='색상 카테고리',
        blank=True
    )
    
    # RGB 값
    rgb_r = models.IntegerField(verbose_name='Red')
    rgb_g = models.IntegerField(verbose_name='Green')
    rgb_b = models.IntegerField(verbose_name='Blue')
    
    # HSL 값
    hsl_h = models.IntegerField(verbose_name='Hue', null=True, blank=True)
    hsl_s = models.IntegerField(verbose_name='Saturation', null=True, blank=True)
    hsl_l = models.IntegerField(verbose_name='Lightness', null=True, blank=True)
    
    meaning = models.TextField(
        verbose_name='색상의 의미',
        blank=True
    )
    fortune_keywords = models.JSONField(
        default=list,
        verbose_name='운세 관련 키워드'
    )
    
    class Meta:
        db_table = 'color_master'
        verbose_name = '색상 마스터'
        verbose_name_plural = '색상 마스터'
    
    def __str__(self):
        return f"{self.color_name} ({self.color_code})"


class MBTISpeechTemplate(models.Model):
    """MBTI별 말투 템플릿"""
    
    CATEGORY_CHOICES = [
        ('greeting', '인사말'),
        ('fortune_good', '좋은 운세'),
        ('fortune_bad', '나쁜 운세'),
        ('recommendation', '추천'),
        ('encouragement', '격려'),
        ('advice', '조언'),
    ]
    
    TONE_CHOICES = [
        ('formal', '격식체'),
        ('casual', '편안한'),
        ('friendly', '친근한'),
    ]
    
    mbti_type = models.CharField(
        max_length=4,
        verbose_name='MBTI 유형'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='카테고리'
    )
    template_text = models.TextField(
        verbose_name='템플릿 텍스트'
    )
    tone = models.CharField(
        max_length=20,
        choices=TONE_CHOICES,
        default='friendly',
        verbose_name='어조'
    )
    
    class Meta:
        db_table = 'mbti_speech_templates'
        unique_together = ['mbti_type', 'category']
        verbose_name = 'MBTI 말투 템플릿'
        verbose_name_plural = 'MBTI 말투 템플릿'
    
    def __str__(self):
        return f"{self.mbti_type} - {self.get_category_display()}"
