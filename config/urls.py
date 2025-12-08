"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from core.views import home, api_root, vue_app

router = routers.DefaultRouter()

urlpatterns = [
    path('', home, name='home'),  # 홈페이지
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),  # API 루트

    # ===== REST API (Vue 프론트엔드용) =====
    path('api/auth/', include('users.api_urls')),           # 인증 API
    path('api/fortune/', include('fortune.api_urls')),      # 운세 API
    path('api/recommendations/', include('recommendations.api_urls')),  # 추천 API
    path('api/items/', include('items.api_urls')),          # 아이템 API

    # ===== 기존 템플릿 뷰 (레거시) =====
    path('users/', include('users.urls')),
    path('fortune/', include('fortune.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('items/', include('items.urls')),

    # Vue SPA (모든 /vue/* 경로를 Vue 앱으로)
    re_path(r'^vue/.*$', vue_app, name='vue-app'),
]

# Development media files serving
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
