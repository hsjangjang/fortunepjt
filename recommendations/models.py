from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class DailyRecommendation(models.Model):
    """일일 추천 기록"""
    
    RECOMMENDATION_TYPES = [
        ('OOTD', 'OOTD'),
        ('MENU', '메뉴'),
        ('ITEM', '아이템'),
        ('ACTIVITY', '활동'),
    ]
    
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
        verbose_name='세션 키'
    )
    recommendation_date = models.DateField(
        verbose_name='추천 날짜',
        db_index=True
    )
    recommendation_type = models.CharField(
        max_length=10,
        choices=RECOMMENDATION_TYPES,
        verbose_name='추천 타입'
    )
    recommendation_data = models.JSONField(
        verbose_name='추천 상세 데이터'
    )
    weather_data = models.JSONField(
        default=dict,
        verbose_name='날씨 정보'
    )
    user_feedback = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name='사용자 평점'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_recommendations'
        verbose_name = '일일 추천'
        verbose_name_plural = '일일 추천'
        indexes = [
            models.Index(fields=['recommendation_date', 'user']),
            models.Index(fields=['recommendation_date', 'session_key']),
        ]
    
    def __str__(self):
        return f"{self.recommendation_date} - {self.get_recommendation_type_display()}"


class OOTDRecommendation(models.Model):
    """OOTD 추천 상세"""
    
    SLEEVE_TYPES = [
        ('SHORT', '반팔'),
        ('LONG', '긴팔'),
        ('SLEEVELESS', '민소매'),
    ]
    
    recommendation = models.ForeignKey(
        DailyRecommendation,
        on_delete=models.CASCADE,
        related_name='ootd_details',
        verbose_name='추천'
    )
    top_color = models.CharField(
        max_length=7,
        verbose_name='상의 색상'
    )
    bottom_color = models.CharField(
        max_length=7,
        verbose_name='하의 색상'
    )
    outer_required = models.BooleanField(
        default=False,
        verbose_name='아우터 필요'
    )
    outer_color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name='아우터 색상'
    )
    sleeve_type = models.CharField(
        max_length=10,
        choices=SLEEVE_TYPES,
        verbose_name='소매 타입'
    )
    style_tags = models.JSONField(
        default=list,
        verbose_name='스타일 태그'
    )
    matching_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='매칭 점수'
    )
    
    class Meta:
        db_table = 'ootd_recommendations'
        verbose_name = 'OOTD 추천'
        verbose_name_plural = 'OOTD 추천'
    
    def __str__(self):
        return f"{self.recommendation.recommendation_date} OOTD"


class MenuRecommendation(models.Model):
    """메뉴 추천 상세"""
    
    CATEGORY_CHOICES = [
        ('korean', '한식'),
        ('chinese', '중식'),
        ('japanese', '일식'),
        ('western', '양식'),
        ('asian', '아시안'),
        ('snack', '분식'),
        ('cafe', '카페'),
        ('etc', '기타'),
    ]
    
    recommendation = models.ForeignKey(
        DailyRecommendation,
        on_delete=models.CASCADE,
        related_name='menu_details',
        verbose_name='추천'
    )
    menu_name = models.CharField(
        max_length=200,
        verbose_name='메뉴 이름'
    )
    menu_category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='메뉴 카테고리'
    )
    menu_color_match = models.JSONField(
        default=dict,
        verbose_name='색상 매칭 정보'
    )
    calories = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='칼로리'
    )
    recipe_link = models.URLField(
        blank=True,
        verbose_name='레시피 링크'
    )
    restaurant_suggestion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='추천 식당'
    )
    
    class Meta:
        db_table = 'menu_recommendations'
        verbose_name = '메뉴 추천'
        verbose_name_plural = '메뉴 추천'
    
    def __str__(self):
        return f"{self.menu_name} - {self.recommendation.recommendation_date}"


class UserPreference(models.Model):
    """사용자 선호도 학습"""
    
    PREFERENCE_TYPES = [
        ('color', '색상'),
        ('style', '스타일'),
        ('food', '음식'),
        ('activity', '활동'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='사용자'
    )
    preference_type = models.CharField(
        max_length=50,
        choices=PREFERENCE_TYPES,
        verbose_name='선호도 타입'
    )
    preference_value = models.CharField(
        max_length=200,
        verbose_name='선호 값'
    )
    score = models.FloatField(
        default=0,
        verbose_name='선호도 점수'
    )
    interaction_count = models.IntegerField(
        default=0,
        verbose_name='상호작용 횟수'
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='마지막 업데이트'
    )
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = '사용자 선호도'
        verbose_name_plural = '사용자 선호도'
        unique_together = ['user', 'preference_type', 'preference_value']
        indexes = [
            models.Index(fields=['user', 'preference_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_preference_type_display()}: {self.preference_value}"
