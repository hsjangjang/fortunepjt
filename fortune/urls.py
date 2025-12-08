from django.urls import path
from . import views

app_name = 'fortune'

urlpatterns = [
    # 운세 조회 (기존 템플릿 뷰 - 레거시)
    path('today/', views.TodayFortuneView.as_view(), name='today'),
    path('calculate/', views.CalculateFortuneView.as_view(), name='calculate'),
    path('detail/', views.DetailFortuneView.as_view(), name='detail'),
    path('item-check/', views.ItemCheckView.as_view(), name='item_check'),
    path('loading/', views.LoadingView.as_view(), name='loading'),
    path('loading/auto/', views.LoadingView.as_view(), name='loading_auto'),
    path('reset/', views.ResetFortuneView.as_view(), name='reset'),

    # API 엔드포인트는 /api/fortune/로 이동
]
