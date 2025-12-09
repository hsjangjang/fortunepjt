from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserItem


class ItemListAPIView(APIView):
    """아이템 목록 조회/생성 API"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """아이템 목록 조회"""
        items = UserItem.objects.filter(user=request.user).order_by('-created_at')

        # 필터링
        category = request.query_params.get('category')
        if category:
            items = items.filter(main_category=category)

        favorite_only = request.query_params.get('favorite')
        if favorite_only == 'true':
            items = items.filter(is_favorite=True)

        items_data = [
            {
                'id': item.id,
                'item_name': item.item_name,
                'main_category': item.main_category,
                'sub_categories': item.sub_categories,
                'image': item.image.url if item.image else None,
                'image_url': item.image.url if item.image else None,
                'dominant_colors': item.dominant_colors,
                'colors_json': item.colors_json,
                'ai_analysis': item.ai_analysis_result,
                'is_favorite': item.is_favorite,
                'created_at': item.created_at.isoformat()
            }
            for item in items
        ]

        return Response({
            'success': True,
            'count': len(items_data),
            'items': items_data
        })

    def post(self, request):
        """아이템 생성"""
        image = request.FILES.get('image')
        if not image:
            return Response({
                'success': False,
                'error': '이미지를 업로드해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 이미지 분석 (업로드 파일 직접 처리 - 임시 파일 관리 내장)
            from .color_analyzer import ImageColorAnalyzer
            analyzer = ImageColorAnalyzer()
            analysis_result = analyzer.analyze_from_file_or_upload(image)

            # 아이템 생성
            item = UserItem.objects.create(
                user=request.user,
                image=image,
                item_name=request.data.get('item_name', '새 아이템'),
                main_category=request.data.get('main_category', 'etc'),
                sub_categories=request.data.getlist('sub_categories', []),
            )

            if analysis_result.get('success'):
                item.dominant_colors = analysis_result['colors']
                item.ai_analysis_result = analysis_result.get('ai_analysis', {})
                item.save()

            return Response({
                'success': True,
                'message': '아이템이 등록되었습니다.',
                'item': {
                    'id': item.id,
                    'item_name': item.item_name,
                    'image_url': item.image.url,
                    'dominant_colors': item.dominant_colors,
                    'ai_analysis': item.ai_analysis_result
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            print(f"[ItemListAPIView] Error: {str(e)}")
            print(traceback.format_exc())
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemDetailAPIView(APIView):
    """아이템 상세 조회/수정/삭제 API"""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return UserItem.objects.get(pk=pk, user=user)
        except UserItem.DoesNotExist:
            return None

    def get(self, request, pk):
        """아이템 상세 조회"""
        item = self.get_object(pk, request.user)
        if not item:
            return Response({
                'success': False,
                'error': '아이템을 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'item': {
                'id': item.id,
                'item_name': item.item_name,
                'main_category': item.main_category,
                'sub_categories': item.sub_categories,
                'image_url': item.image.url if item.image else None,
                'dominant_colors': item.dominant_colors,
                'ai_analysis': item.ai_analysis_result,
                'is_favorite': item.is_favorite,
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat()
            }
        })

    def put(self, request, pk):
        """아이템 수정"""
        item = self.get_object(pk, request.user)
        if not item:
            return Response({
                'success': False,
                'error': '아이템을 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        # 수정 가능한 필드들
        if 'item_name' in request.data:
            item.item_name = request.data['item_name']
        if 'main_category' in request.data:
            item.main_category = request.data['main_category']
        if 'sub_categories' in request.data:
            item.sub_categories = request.data['sub_categories']
        if 'is_favorite' in request.data:
            item.is_favorite = request.data['is_favorite']

        item.save()

        return Response({
            'success': True,
            'message': '아이템이 수정되었습니다.',
            'item': {
                'id': item.id,
                'item_name': item.item_name,
                'is_favorite': item.is_favorite
            }
        })

    def delete(self, request, pk):
        """아이템 삭제"""
        item = self.get_object(pk, request.user)
        if not item:
            return Response({
                'success': False,
                'error': '아이템을 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({
            'success': True,
            'message': '아이템이 삭제되었습니다.'
        })


class ItemAnalyzeAPIView(APIView):
    """이미지 분석 API (임시 분석)"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """이미지 분석만 수행 (저장하지 않음)"""
        image = request.FILES.get('image')
        if not image:
            return Response({
                'success': False,
                'error': '이미지를 업로드해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .color_analyzer import ImageColorAnalyzer
            analyzer = ImageColorAnalyzer()
            analysis_result = analyzer.analyze_from_file_or_upload(image)

            # API 할당량 초과 에러 체크
            if not analysis_result.get('success') and analysis_result.get('error_type') == 'quota_exceeded':
                return Response({
                    'success': False,
                    'error': analysis_result.get('message', 'AI 분석 서비스가 일시적으로 제한되었습니다.'),
                    'error_type': 'quota_exceeded'
                }, status=503)

            # 카테고리 추천
            ai_category = analysis_result.get('ai_analysis', {}).get('category', '')
            ai_item_name = analysis_result.get('ai_analysis', {}).get('item_name', '')
            category_mapping = {
                'wallet': '지갑', 'keyring': '키링', 'doll': '인형',
                'electronics': '전자기기', 'clothing': '의류',
                'accessory': '액세서리', 'food': '음식', 'etc': '기타'
            }

            # 아이템명 결정 (item_name 우선)
            if ai_item_name:
                item_name_display = ai_item_name
            elif ai_category in category_mapping.values():
                item_name_display = ai_category
            else:
                item_name_display = category_mapping.get(ai_category.lower(), ai_category) if ai_category else '아이템'

            return Response({
                'success': True,
                'analysis': analysis_result,
                'suggested_name': item_name_display,
                'item_name': item_name_display
            })

        except Exception as e:
            import traceback
            print(f"[ItemAnalyzeAPIView] Error: {str(e)}")
            print(traceback.format_exc())
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemFavoriteAPIView(APIView):
    """아이템 즐겨찾기 토글 API"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """즐겨찾기 토글"""
        try:
            item = UserItem.objects.get(pk=pk, user=request.user)
            item.is_favorite = not item.is_favorite
            item.save()

            return Response({
                'success': True,
                'is_favorite': item.is_favorite,
                'message': '즐겨찾기에 추가되었습니다.' if item.is_favorite else '즐겨찾기에서 제거되었습니다.'
            })
        except UserItem.DoesNotExist:
            return Response({
                'success': False,
                'error': '아이템을 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
