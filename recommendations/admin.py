from django.contrib import admin
from .models import DailyRecommendation, OOTDRecommendation, MenuRecommendation, UserPreference

@admin.register(DailyRecommendation)
class DailyRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'recommendation_date', 'recommendation_type', 'user_feedback']
    list_filter = ['recommendation_date', 'recommendation_type', 'user_feedback']
    search_fields = ['user__username', 'session_key']
    date_hierarchy = 'recommendation_date'

@admin.register(OOTDRecommendation)
class OOTDRecommendationAdmin(admin.ModelAdmin):
    list_display = ['recommendation', 'top_color', 'bottom_color', 'outer_required', 'matching_score']
    list_filter = ['outer_required', 'sleeve_type']

@admin.register(MenuRecommendation)
class MenuRecommendationAdmin(admin.ModelAdmin):
    list_display = ['recommendation', 'menu_name', 'menu_category']
    list_filter = ['menu_category']
    search_fields = ['menu_name', 'restaurant_suggestion']

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'preference_type', 'preference_value', 'score', 'interaction_count']
    list_filter = ['preference_type']
    search_fields = ['user__username', 'preference_value']
