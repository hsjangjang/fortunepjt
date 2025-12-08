from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
    # 아이템 관리
    path('', views.ItemListView.as_view(), name='list'),
    path('upload/', views.ItemUploadView.as_view(), name='upload'),
    path('<int:pk>/', views.ItemDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.ItemDeleteView.as_view(), name='delete'),
    
    # 색상 분석
    path('analyze/', views.ColorAnalysisView.as_view(), name='analyze'),
    path('match/', views.ColorMatchView.as_view(), name='match'),
]
