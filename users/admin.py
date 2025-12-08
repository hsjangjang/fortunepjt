from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'birth_date', 'gender', 'mbti', 'personal_color']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {
            'fields': ('birth_date', 'birth_time', 'gender', 'chinese_name', 'mbti', 'personal_color', 'phone_number', 'profile_image')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('birth_date', 'gender')
        }),
    )
