from django.contrib import admin
from django.utils import timezone
from .models import DailyFortuneCache, WeeklyFortuneCache, MonthlyFortuneCache, FortuneBaseData, ColorMaster, MBTISpeechTemplate

@admin.register(DailyFortuneCache)
class DailyFortuneCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'fortune_date', 'fortune_score', 'lucky_color', 'created_at_display', 'birth_date']
    list_filter = ['fortune_date', 'fortune_score']
    search_fields = ['user__username', 'session_key']
    date_hierarchy = 'fortune_date'
    ordering = ['-created_at']

    def created_at_display(self, obj):
        """생성일시를 초 단위까지 표시 (KST)"""
        if obj.created_at:
            # UTC를 KST로 변환
            from django.utils import timezone
            import pytz
            kst = pytz.timezone('Asia/Seoul')
            local_time = obj.created_at.astimezone(kst)
            return local_time.strftime('%Y-%m-%d %H:%M:%S')
        return '-'
    created_at_display.short_description = '생성일시 (KST)'
    created_at_display.admin_order_field = 'created_at'

@admin.register(FortuneBaseData)
class FortuneBaseDataAdmin(admin.ModelAdmin):
    list_display = ['category', 'code', 'name_ko', 'name_cn']
    list_filter = ['category']
    search_fields = ['name_ko', 'name_cn', 'code']

@admin.register(ColorMaster)
class ColorMasterAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'color_code', 'color_category']
    list_filter = ['color_category']
    search_fields = ['color_name', 'color_code']

@admin.register(WeeklyFortuneCache)
class WeeklyFortuneCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'year', 'week_number', 'birth_date', 'created_at_display']
    list_filter = ['year', 'week_number']
    search_fields = ['user__username', 'session_key']
    ordering = ['-year', '-week_number', '-created_at']

    def created_at_display(self, obj):
        """생성일시를 초 단위까지 표시 (KST)"""
        if obj.created_at:
            # UTC를 KST로 변환
            from django.utils import timezone
            import pytz
            kst = pytz.timezone('Asia/Seoul')
            local_time = obj.created_at.astimezone(kst)
            return local_time.strftime('%Y-%m-%d %H:%M:%S')
        return '-'
    created_at_display.short_description = '생성일시 (KST)'
    created_at_display.admin_order_field = 'created_at'


@admin.register(MonthlyFortuneCache)
class MonthlyFortuneCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'year', 'month', 'birth_date', 'created_at_display']
    list_filter = ['year', 'month']
    search_fields = ['user__username', 'session_key']
    ordering = ['-year', '-month', '-created_at']

    def created_at_display(self, obj):
        """생성일시를 초 단위까지 표시 (KST)"""
        if obj.created_at:
            # UTC를 KST로 변환
            from django.utils import timezone
            import pytz
            kst = pytz.timezone('Asia/Seoul')
            local_time = obj.created_at.astimezone(kst)
            return local_time.strftime('%Y-%m-%d %H:%M:%S')
        return '-'
    created_at_display.short_description = '생성일시 (KST)'
    created_at_display.admin_order_field = 'created_at'


@admin.register(MBTISpeechTemplate)
class MBTISpeechTemplateAdmin(admin.ModelAdmin):
    list_display = ['mbti_type', 'category', 'tone']
    list_filter = ['mbti_type', 'category', 'tone']
    search_fields = ['mbti_type', 'template_text']
