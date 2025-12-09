from django.contrib import admin
from .models import UserItem

@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_name', 'main_category', 'is_favorite', 'created_at']
    list_filter = ['main_category', 'is_favorite']
    search_fields = ['user__username', 'item_name']
    date_hierarchy = 'created_at'
