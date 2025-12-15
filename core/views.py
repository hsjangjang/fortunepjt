from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


def home(request):
    """Health check 및 API 루트"""
    return JsonResponse({
        "status": "ok",
        "message": "Fortune Service API",
        "api_root": "/api/"
    })

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
