from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date

def home(request):
    """홈페이지 - 템플릿 렌더링"""
    context = {
        'today_fortune': None  # 로그인한 사용자의 오늘 운세
    }

    # 로그인한 사용자의 오늘 운세 가져오기 (추후 구현)
    if request.user.is_authenticated:
        # context['today_fortune'] = get_user_fortune(request.user)
        pass

    return render(request, 'index.html', context)

def vue_app(request):
    """Vue SPA 서빙"""
    context = {
        'debug': settings.DEBUG
    }
    return render(request, 'vue_app.html', context)

@api_view(['GET'])
def api_root(request):
    """API 루트 - 사용 가능한 엔드포인트 목록"""
    return Response({
        "message": "🔮 Fortune Service API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "logout": "/api/auth/logout/",
                "profile": "/api/auth/profile/",
            },
            "fortune": {
                "today": "/api/fortune/today/",
                "calculate": "/api/fortune/calculate/",
                "history": "/api/fortune/history/",
                "colors": "/api/fortune/colors/",
                "lucky_colors": "/api/fortune/lucky-colors/",
            },
            "recommendations": {
                "ootd": "/api/recommendations/ootd/",
                "menu": "/api/recommendations/menu/",
                "item": "/api/recommendations/item/",
                "feedback": "/api/recommendations/feedback/",
            },
            "items": {
                "list": "/api/items/",
                "upload": "/api/items/upload/",
                "analyze": "/api/items/analyze/",
                "match": "/api/items/match/",
            }
        },
        "documentation": "Visit /admin/ for Django Admin",
        "note": "Most endpoints require authentication or session key"
    })
