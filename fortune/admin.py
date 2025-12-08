from django.contrib import admin
from .models import DailyFortuneCache, FortuneBaseData, ColorMaster, MBTISpeechTemplate

@admin.register(DailyFortuneCache)
class DailyFortuneCacheAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'fortune_date', 'fortune_score', 'lucky_color']
    list_filter = ['fortune_date', 'fortune_score']
    search_fields = ['user__username', 'session_key']
    date_hierarchy = 'fortune_date'

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

@admin.register(MBTISpeechTemplate)
class MBTISpeechTemplateAdmin(admin.ModelAdmin):
    list_display = ['mbti_type', 'category', 'tone']
    list_filter = ['mbti_type', 'category', 'tone']
