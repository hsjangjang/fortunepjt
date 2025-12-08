from django.db import models
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserItem(models.Model):
    """사용자 아이템"""
    
    # 기존 CATEGORY_CHOICES - 마이그레이션 후 삭제 예정
    CATEGORY_CHOICES = [
        ('top', '상의'),
        ('bottom', '하의'),
        ('outer', '아우터'),
        ('dress', '원피스'),
        ('shoes', '신발'),
        ('bag', '가방'),
        ('accessory', '악세서리'),
        ('etc', '기타'),
    ]
    
    # 새로운 카테고리 구조
    MAIN_CATEGORY_CHOICES = [
        ('clothing', '의류'),
        ('cosmetics', '화장품'),
        ('electronics', '전자제품'),
        ('accessories', '악세서리'),
        ('etc', '기타'),
    ]
    
    # 소분류 매핑
    SUB_CATEGORY_MAP = {
        'clothing': ['상의', '하의', '아우터', '원피스', '신발', '가방'],
        'cosmetics': ['스킨케어', '메이크업', '헤어'],
        'electronics': ['스마트폰', '태블릿', '노트북', '이어폰'],
        'accessories': ['귀걸이', '목걸이', '반지', '팔찌'],
        'etc': []  # 빈 배열 = 사용자 직접 입력
    }
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='사용자'
    )
    item_name = models.CharField(
        max_length=200,
        verbose_name='아이템 이름'
    )
    
    # 기존 필드 - 마이그레이션 후 삭제 예정
    item_category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='카테고리',
        null=True,
        blank=True
    )
    
    # 새로운 필드
    main_category = models.CharField(
        max_length=50,
        choices=MAIN_CATEGORY_CHOICES,
        verbose_name='대분류',
        null=True,
        blank=True
    )
    sub_categories = models.JSONField(
        default=list,
        verbose_name='소분류 (목록)',
        help_text='소분류 목록 또는 기타 카테고리의 경우 사용자 입력값'
    )
    
    image = models.ImageField(
        upload_to='items/%Y/%m/',
        verbose_name='이미지'
    )
    image_url = models.URLField(
        blank=True,
        verbose_name='이미지 URL'
    )
    dominant_colors = models.JSONField(
        default=list,
        verbose_name='주요 색상들'
    )
    ai_analysis_result = models.JSONField(
        default=dict,
        verbose_name='AI 분석 결과'
    )
    is_favorite = models.BooleanField(
        default=False,
        verbose_name='즐겨찾기'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_items'
        verbose_name = '사용자 아이템'
        verbose_name_plural = '사용자 아이템'
        indexes = [
            models.Index(fields=['user', 'item_category']),
            models.Index(fields=['user', 'main_category']),
            models.Index(fields=['user', 'is_favorite']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.item_name}"
    
    @property
    def primary_color(self):
        """가장 주요한 색상 반환"""
        if self.dominant_colors:
            return self.dominant_colors[0].get('color', '#000000')
        return '#000000'

    @property
    def colors_json(self):
        """색상 정보를 JSON 문자열로 반환"""
        import json
        return json.dumps(self.dominant_colors or [])

    @property
    def ai_analysis_json(self):
        """AI 분석 결과를 JSON 문자열로 반환"""
        import json
        return json.dumps(self.ai_analysis_result or {})
