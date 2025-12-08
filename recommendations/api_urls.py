from django.urls import path
from . import api_views

app_name = 'recommendations_api'

urlpatterns = [
    # OOTD 추천
    path('ootd/', api_views.OOTDRecommendationAPIView.as_view(), name='ootd'),

    # 메뉴 추천
    path('menu/', api_views.MenuRecommendationAPIView.as_view(), name='menu'),

    # 날씨 정보
    path('weather/', api_views.WeatherAPIView.as_view(), name='weather'),
]
