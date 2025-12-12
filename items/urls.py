# items/urls.py
# 레거시 템플릿 뷰 URL - 기본 리다이렉트만 제공
# API 엔드포인트: items/api_urls.py 사용

from django.urls import path
from django.views.generic import RedirectView

app_name = 'items'

# 레거시 URL은 Vue 프론트엔드로 리다이렉트 (NoReverseMatch 방지)
urlpatterns = [
    path('upload/', RedirectView.as_view(url='/vue/items/upload', permanent=False), name='upload'),
    path('', RedirectView.as_view(url='/vue/items', permanent=False), name='list'),
]
