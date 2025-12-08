from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # OOTD 추천
    path('ootd/', views.OOTDRecommendationView.as_view(), name='ootd'),
    
    # 메뉴 추천
    # path('menu/', views.MenuRecommendationView.as_view(), name='menu'),
    path('menu/', views.menu_recommendation, name='menu'),
    
    # 아이템 추천
    path('item/', views.ItemRecommendationView.as_view(), name='item'),
    
    # 피드백
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    
    # 위치 기반 날씨 API
    path('weather/location/', views.WeatherLocationView.as_view(), name='weather-location'),
]
