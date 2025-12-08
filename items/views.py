from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response

# @method_decorator(login_required, name='dispatch')
class ItemListView(ListView):
    model = None # Will be set in get_queryset
    template_name = 'items/list.html'
    context_object_name = 'items'
    
    def get_queryset(self):
        from .models import UserItem
        # return UserItem.objects.filter(user=self.request.user).order_by('-created_at')
        if self.request.user.is_authenticated:
            return UserItem.objects.filter(user=self.request.user).order_by('-created_at')
        return UserItem.objects.none()  # 비로그인 시 빈 목록
    
@method_decorator(login_required, name='dispatch')
class ItemUploadView(TemplateView):
    template_name = 'items/upload.html'

    def _translate_category(self, category):
        """AI 카테고리 정규화 (이미 한글이면 그대로 반환, 영문이면 한글로 변환)"""
        # AI가 한글로 응답하는 경우가 대부분이므로 그대로 반환
        if category in ['지갑', '키링', '인형', '전자기기', '의류', '액세서리', '음식', '기타']:
            return category

        # 영문으로 응답한 경우 변환
        category_map = {
            'wallet': '지갑',
            'keyring': '키링',
            'doll': '인형',
            'electronics': '전자기기',
            'clothing': '의류',
            'accessory': '액세서리',
            'food': '음식',
            'etc': '기타'
        }
        return category_map.get(category.lower(), category)

    def post(self, request):
        # AJAX 요청 체크
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('is_temporary')
        
        image = request.FILES.get('image')
        if not image:
            if is_ajax:
                return JsonResponse({'success': False, 'message': '이미지를 업로드해주세요.'})
            messages.error(request, '이미지를 업로드해주세요.')
            return redirect('items:upload')
            
        try:
            # 1. 아이템 저장 (먼저 저장해야 파일 경로가 생성됨)
            from .models import UserItem
            
            # 임시 분석용인 경우 아이템을 저장하지 않고 분석만 수행
            is_temp = request.POST.get('is_temporary') == 'true'
            
            if is_temp:
                # 임시 파일로 분석만 수행
                import tempfile
                import os
                from django.core.files.storage import default_storage
                
                # 임시 파일 저장
                temp_path = default_storage.save(f'temp/{image.name}', image)
                full_path = default_storage.path(temp_path)
                
                try:
                    # AI 분석
                    from .color_analyzer import ImageColorAnalyzer
                    analyzer = ImageColorAnalyzer()
                    analysis_result = analyzer.analyze_image_with_ai(full_path)

                    # AI가 감지한 카테고리를 아이템명으로 사용
                    ai_category = analysis_result.get('ai_analysis', {}).get('category', '')

                    # 아이템명 결정 로직
                    if ai_category:
                        # AI가 카테고리를 감지한 경우
                        item_name_display = self._translate_category(ai_category)
                    elif analysis_result.get('method') == 'pillow':
                        # Pillow fallback인 경우 - 색상 기반 기본명
                        colors = analysis_result.get('colors', [])
                        if colors:
                            color_name = colors[0].get('korean_name', '알 수 없는')
                            item_name_display = f'{color_name} 아이템'
                        else:
                            item_name_display = '분석된 아이템'
                    else:
                        # 기타 경우
                        item_name_display = '업로드된 아이템'

                    return JsonResponse({
                        'success': True,
                        'analysis': analysis_result,
                        'item_name': item_name_display
                    })
                finally:
                    # 파일 삭제 (반드시 실행)
                    try:
                        import time
                        time.sleep(0.1)  # 짧은 대기로 파일 잠금 해제
                        default_storage.delete(temp_path)
                    except Exception as cleanup_error:
                        print(f"임시 파일 삭제 실패 (무시): {cleanup_error}")
            
            # 정상 업로드
            # 카테고리 데이터 추출
            main_category = request.POST.get('main_category', 'etc')
            sub_categories_raw = request.POST.getlist('sub_categories[]')  # 체크박스 배열
            custom_input = request.POST.get('custom_category', '').strip()  # 기타 직접입력
            
            # 소분류 결정
            if main_category == 'etc' and custom_input:
                sub_categories = [custom_input]  # 기타는 사용자 직접 입력
            else:
                sub_categories = sub_categories_raw  # 선택된 소분류들
            
            item = UserItem.objects.create(
                user=request.user,
                image=image,
                item_name=request.POST.get('item_name', '새 아이템'),
                main_category=main_category,
                sub_categories=sub_categories,
                # item_category는 하위 호환성을 위해 임시로 유지
                item_category=request.POST.get('category', 'etc')
            )
            
            # 2. 이미지 분석 (AI 우선, 실패 시 기본 분석)
            from .color_analyzer import ImageColorAnalyzer
            analyzer = ImageColorAnalyzer()
            
            # AI 분석 시도
            analysis_result = analyzer.analyze_image_with_ai(item.image.path)
            
            if analysis_result['success']:
                # 3. 분석 결과 저장
                item.dominant_colors = analysis_result['colors']
                item.ai_analysis_result = analysis_result.get('ai_analysis', {})
                # Note: AI analysis stored for reference but does not override user's item_name
                item.save()
                
                messages.success(request, f'아이템이 성공적으로 등록되었습니다. (AI 분석 완료: {analysis_result.get("method", "gemini")})')
            else:
                messages.warning(request, '이미지 분석에 실패했지만 아이템은 등록되었습니다.')
                
            return redirect('items:detail', pk=item.pk)
            
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})
            messages.error(request, f'오류가 발생했습니다: {str(e)}')
            return redirect('items:upload')

from django.views.generic import TemplateView, ListView, DetailView

# ... (existing imports)

@method_decorator(login_required, name='dispatch')
class ItemDetailView(DetailView):
    model = None # Will be set in get_queryset
    template_name = 'items/detail.html'
    context_object_name = 'item'
    
    def get_queryset(self):
        from .models import UserItem
        return UserItem.objects.filter(user=self.request.user)

@method_decorator(login_required, name='dispatch')
class ItemDeleteView(APIView):
    def delete(self, request, pk):
        try:
            from .models import UserItem
            item = UserItem.objects.get(pk=pk, user=request.user)
            item.delete()
            return Response({"success": True, "message": "아이템이 삭제되었습니다."})
        except UserItem.DoesNotExist:
            return Response({"success": False, "message": "아이템을 찾을 수 없습니다."}, status=404)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=500)

@method_decorator(login_required, name='dispatch')
class ColorAnalysisView(TemplateView):
    template_name = 'items/analysis.html'

    def _translate_category(self, category):
        """AI 카테고리 정규화"""
        if category in ['지갑', '키링', '인형', '전자기기', '의류', '액세서리', '음식', '기타']:
            return category
        category_map = {
            'wallet': '지갑', 'keyring': '키링', 'doll': '인형',
            'electronics': '전자기기', 'clothing': '의류',
            'accessory': '액세서리', 'food': '음식', 'etc': '기타'
        }
        return category_map.get(category.lower(), category) if category else '아이템'

    def post(self, request):
        """아이템 이미지 분석 API (행운템 분석 페이지용)"""
        image = request.FILES.get('image')
        if not image:
            return JsonResponse({'success': False, 'message': '이미지를 업로드해주세요.'})

        import tempfile
        import os
        temp_path = None

        try:
            from .color_analyzer import ImageColorAnalyzer

            # 임시 파일로 저장 (S3 환경에서도 동작하도록)
            suffix = os.path.splitext(image.name)[1] or '.jpg'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                for chunk in image.chunks():
                    tmp.write(chunk)
                temp_path = tmp.name

            # AI 분석
            analyzer = ImageColorAnalyzer()
            analysis_result = analyzer.analyze_image_with_ai(temp_path)

            # 아이템명 결정
            ai_category = analysis_result.get('ai_analysis', {}).get('category', '')
            ai_item_name = analysis_result.get('ai_analysis', {}).get('item_name', '')

            if ai_item_name:
                item_name_display = ai_item_name
            elif ai_category:
                item_name_display = self._translate_category(ai_category)
            elif analysis_result.get('method') == 'pillow':
                colors = analysis_result.get('colors', [])
                if colors:
                    color_name = colors[0].get('korean_name', '알 수 없는')
                    item_name_display = f'{color_name} 아이템'
                else:
                    item_name_display = '분석된 아이템'
            else:
                item_name_display = '업로드된 아이템'

            return JsonResponse({
                'success': True,
                'analysis': analysis_result,
                'item_name': item_name_display,
                'suggested_name': item_name_display
            })

        except Exception as e:
            import traceback
            print(f"[ColorAnalysis] 오류: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'message': f'분석 오류: {str(e)}'})

        finally:
            # 임시 파일 삭제
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

class ColorMatchView(APIView):
    def post(self, request):
        return Response({"message": "Color match endpoint"})
