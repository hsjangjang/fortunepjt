from django.urls import path
from . import api_views

app_name = 'items_api'

urlpatterns = [
    # 아이템 목록/생성
    path('', api_views.ItemListAPIView.as_view(), name='list'),

    # 이미지 분석 (저장 없이)
    path('analyze/', api_views.ItemAnalyzeAPIView.as_view(), name='analyze'),

    # 아이템 상세/수정/삭제
    path('<int:pk>/', api_views.ItemDetailAPIView.as_view(), name='detail'),

    # 즐겨찾기 토글
    path('<int:pk>/favorite/', api_views.ItemFavoriteAPIView.as_view(), name='favorite'),
]
