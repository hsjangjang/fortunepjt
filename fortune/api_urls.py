from django.urls import path
from . import api_views

app_name = 'fortune_api'

urlpatterns = [
    # 운세 계산 (비로그인 사용자용 - form data 필요)
    path('calculate/', api_views.FortuneCalculateAPIView.as_view(), name='calculate'),

    # 오늘의 운세 조회 (캐시 확인만)
    path('today/', api_views.TodayFortuneAPIView.as_view(), name='today'),

    # 운세 생성 (로그인 사용자용 - 로딩 페이지에서 호출)
    path('generate/', api_views.GenerateFortuneAPIView.as_view(), name='generate'),

    # 아이템 행운도 측정
    path('item-check/', api_views.ItemCheckAPIView.as_view(), name='item_check'),
]
