from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from .models import UserItem
import requests
import numpy as np


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

        # 유저별 순번 계산 (최신순이므로 역순)
        total_count = items.count()
        items_data = [
            {
                'id': item.id,
                'user_order': total_count - idx,  # 유저별 순번 (최신이 가장 큰 번호)
                'item_name': item.item_name,
                'main_category': item.main_category,
                'sub_categories': item.sub_categories,
                'image': item.image.url if item.image else None,
                'image_url': item.image.url if item.image else None,
                'dominant_colors': item.dominant_colors,
                'ai_analysis': item.ai_analysis_result,
                'is_favorite': item.is_favorite,
                'created_at': item.created_at.isoformat()
            }
            for idx, item in enumerate(items)
        ]

        return Response({
            'success': True,
            'count': len(items_data),
            'items': items_data
        })

    def post(self, request):
        """아이템 생성"""
        import json

        image = request.FILES.get('image')
        if not image:
            return Response({
                'success': False,
                'error': '이미지를 업로드해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 이미 분석된 데이터가 있는지 확인 (행운템 분석에서 넘어온 경우)
            pre_analyzed = request.data.get('pre_analyzed') == 'true'

            if pre_analyzed:
                # 이미 분석된 결과 사용 (재분석 스킵)
                try:
                    dominant_colors = json.loads(request.data.get('dominant_colors', '[]'))
                    ai_analysis = json.loads(request.data.get('ai_analysis', '{}'))
                except json.JSONDecodeError:
                    dominant_colors = []
                    ai_analysis = {}

                # 아이템 생성
                item = UserItem.objects.create(
                    user=request.user,
                    image=image,
                    item_name=request.data.get('item_name', '새 아이템'),
                    main_category=request.data.get('main_category', 'etc'),
                    sub_categories=request.data.getlist('sub_categories', []),
                    dominant_colors=dominant_colors,
                    ai_analysis_result=ai_analysis
                )
            else:
                # 새로 분석 수행
                from .item_analyzer import ImageColorAnalyzer
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

        # 유저별 순번 계산 (등록순 기준)
        user_order = UserItem.objects.filter(
            user=request.user,
            created_at__lte=item.created_at
        ).count()

        return Response({
            'success': True,
            'item': {
                'id': item.id,
                'user_order': user_order,  # 유저별 순번
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
            from .item_analyzer import ImageColorAnalyzer
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


class ItemSimilarityAPIView(APIView):
    """GMS Embedding API를 사용한 아이템 유사도 계산"""
    permission_classes = [AllowAny]  # 비로그인 사용자도 사용 가능

    def _get_embeddings(self, texts: list) -> dict:
        """GMS API로 텍스트 임베딩 벡터 조회"""
        gms_api_key = getattr(settings, 'GMS_API_KEY', '')
        gms_api_base = getattr(settings, 'GMS_OPENAI_BASE_URL', 'https://gms.ssafy.io/gmsapi/api.openai.com/v1')

        if not gms_api_key:
            return {'success': False, 'error': 'GMS_API_KEY not configured'}

        try:
            response = requests.post(
                f"{gms_api_base}/embeddings",
                headers={
                    'Authorization': f'Bearer {gms_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'text-embedding-3-small',
                    'input': texts
                },
                timeout=10
            )

            if response.status_code != 200:
                print(f"[ItemSimilarity] GMS API Error: {response.status_code} - {response.text}")
                return {'success': False, 'error': f'API error: {response.status_code}'}

            data = response.json()
            embeddings = [item['embedding'] for item in data['data']]
            return {'success': True, 'embeddings': embeddings}

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'API timeout'}
        except Exception as e:
            print(f"[ItemSimilarity] Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        """코사인 유사도 계산"""
        a = np.array(vec1)
        b = np.array(vec2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def post(self, request):
        """아이템과 행운 아이템 간 유사도 계산"""
        item_name = request.data.get('item_name', '')
        lucky_items = request.data.get('lucky_items', [])

        if not item_name:
            return Response({
                'success': False,
                'error': 'item_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not lucky_items or not isinstance(lucky_items, list):
            return Response({
                'success': False,
                'error': 'lucky_items array is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 모든 텍스트를 한번에 임베딩 (API 호출 1회)
        all_texts = [item_name] + lucky_items
        result = self._get_embeddings(all_texts)

        if not result['success']:
            return Response({
                'success': False,
                'error': result.get('error', 'Embedding failed')
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        embeddings = result['embeddings']
        item_embedding = embeddings[0]
        lucky_embeddings = embeddings[1:]

        # 각 행운 아이템과의 유사도 계산
        similarities = []
        max_similarity = 0
        best_match = None

        for i, lucky_item in enumerate(lucky_items):
            similarity = self._cosine_similarity(item_embedding, lucky_embeddings[i])
            similarities.append({
                'item': lucky_item,
                'similarity': round(similarity, 4)
            })
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = lucky_item

        return Response({
            'success': True,
            'item_name': item_name,
            'max_similarity': round(max_similarity, 4),
            'best_match': best_match,
            'details': similarities
        })
