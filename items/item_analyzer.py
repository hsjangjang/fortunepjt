"""
아이템 이미지 분석 모듈
- 색상 분석: Pillow + 색상 클러스터링
- AI 분석: Gemini 2.5 Flash Vision API (GMS)
  - 아이템 이름 자동 감지
  - 관련 태그 생성
  - 운세별 점수 계산 (love, money, work, health, study)
"""
from PIL import Image

from collections import Counter
import colorsys
import json
import os
import base64

class ItemAnalyzer:
    """아이템 이미지 분석 클래스 (색상 + AI 분석)"""
    
    def __init__(self):
        # 한국어 색상 이름 매핑
        self.color_names = {
            'red': '빨간색',
            'orange': '주황색', 
            'yellow': '노란색',
            'green': '초록색',
            'lightgreen': '연두색',
            'blue': '파란색',
            'skyblue': '하늘색',
            'navy': '남색',
            'purple': '보라색',
            'pink': '분홍색',
            'brown': '갈색',
            'beige': '베이지색',
            'gray': '회색',
            'black': '검은색',
            'white': '흰색'
        }
        
        # RGB 범위별 색상 분류
        self.color_ranges = {
            'red': [(180, 0, 0), (255, 100, 100)],
            'orange': [(255, 140, 0), (255, 200, 100)],
            'yellow': [(200, 200, 0), (255, 255, 150)],
            'green': [(0, 100, 0), (100, 255, 100)],
            'lightgreen': [(100, 200, 100), (200, 255, 200)],
            'blue': [(0, 0, 100), (100, 100, 255)],
            'skyblue': [(100, 150, 200), (200, 230, 255)],
            'navy': [(0, 0, 50), (50, 50, 150)],
            'purple': [(100, 0, 100), (200, 100, 200)],
            'pink': [(200, 100, 150), (255, 200, 230)],
            'brown': [(100, 50, 0), (180, 120, 80)],
            'beige': [(200, 180, 150), (250, 230, 200)],
            'gray': [(100, 100, 100), (200, 200, 200)],
            'black': [(0, 0, 0), (50, 50, 50)],
            'white': [(230, 230, 230), (255, 255, 255)]
        }
    
    def analyze_from_file_or_upload(self, image_source):
        """파일 경로 또는 업로드된 파일 객체에서 분석

        Args:
            image_source: 파일 경로(str) 또는 Django UploadedFile 객체

        Returns:
            분석 결과 dict
        """
        import tempfile
        import os

        temp_path = None
        should_cleanup = False

        try:
            # 이미 파일 경로인 경우
            if isinstance(image_source, str):
                if os.path.exists(image_source):
                    return self.analyze_image_with_ai(image_source)
                else:
                    # S3 URL이거나 존재하지 않는 경로
                    raise ValueError(f"파일을 찾을 수 없습니다: {image_source}")

            # Django UploadedFile 또는 파일 객체인 경우 -> 임시 파일 생성
            file_name = getattr(image_source, 'name', 'image.jpg')
            suffix = os.path.splitext(file_name)[1] or '.jpg'

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                # 파일 포인터 리셋 (이미 읽었을 수 있음)
                if hasattr(image_source, 'seek'):
                    image_source.seek(0)

                # chunks() 메서드가 있으면 사용 (Django UploadedFile)
                if hasattr(image_source, 'chunks'):
                    for chunk in image_source.chunks():
                        tmp.write(chunk)
                else:
                    # 일반 파일 객체
                    tmp.write(image_source.read())

                temp_path = tmp.name
                should_cleanup = True

            # 분석 수행
            result = self.analyze_image_with_ai(temp_path)

            # 파일 포인터 리셋 (나중에 저장할 때 필요)
            if hasattr(image_source, 'seek'):
                image_source.seek(0)

            return result

        finally:
            # 임시 파일 정리
            if should_cleanup and temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def analyze_image_with_ai(self, image_path):
        """Gemini 2.5 Flash Vision API를 사용한 AI 이미지 분석 (GMS)"""
        print(f"[DEBUG] AI 분석 시작: {image_path}")
        try:
            import requests
            from django.conf import settings

            # GMS API 설정 (Gemini 모델용 URL 사용)
            api_key = getattr(settings, 'GMS_API_KEY', '')
            # GMS Gemini URL: gemini.googleapis.com (NOT generativelanguage)
            gemini_base_url = getattr(settings, 'GMS_GEMINI_BASE_URL', 'https://gms.ssafy.io/gmsapi/gemini.googleapis.com/v1beta')

            print(f"[DEBUG] GMS API 키 확인: {api_key[:10]}..." if api_key else "[DEBUG] API 키 없음!")
            print(f"[DEBUG] GMS Gemini Base URL: {gemini_base_url}")

            if not api_key:
                raise ValueError("GMS_API_KEY not configured")

            # 이미지 리사이징 (GMS 프록시 body size 제한 회피)
            img = Image.open(image_path)

            # 이미지를 512px로 줄임 (GMS 프록시 제한 회피)
            max_size = 512
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # RGB로 변환 (RGBA인 경우)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # 메모리에 저장 (quality 60으로 용량 최소화)
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=60)
            image_data = buffer.getvalue()

            print(f"[DEBUG] 이미지 크기: {len(image_data)} bytes, {img.width}x{img.height}")

            base64_image = base64.b64encode(image_data).decode('utf-8')

            # MIME 타입은 항상 JPEG (리사이징 후 JPEG로 변환됨)
            mime_type = 'image/jpeg'

            prompt = """이미지의 물체를 분석해 JSON으로 응답.

{
  "item_name": "물체이름(한글2-4자)",
  "primary_color": "색상",
  "secondary_colors": [],
  "tags": ["종류", "운세", "느낌"],
  "fortune_scores": {"love": 50, "money": 50, "work": 50, "health": 50, "study": 50}
}

색상 규칙:
- 연한파랑/민트/청록 → 하늘색
- 진한파랑 → 파란색
- 짙은파랑 → 남색
색상목록: 빨간색,주황색,노란색,초록색,파란색,보라색,분홍색,갈색,베이지색,회색,검은색,흰색,남색,하늘색,금색

배경무시. JSON만."""

            # Gemini API 요청 데이터 구성
            request_data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 1000
                }
            }

            # API 엔드포인트 목록 (fallback 방식)
            api_endpoints = [
                # 1차: gemini-2.5-flash (이전에 작동하던 모델)
                (gemini_base_url, "gemini-2.5-flash"),
                # 2차: gemini-2.0-flash
                (gemini_base_url, "gemini-2.0-flash"),
                # 3차 fallback: generativelanguage + gemini-2.0-flash-exp
                ("https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta", "gemini-2.0-flash-exp-image-generation"),
            ]

            response = None
            last_error = None

            for base_url, model_name in api_endpoints:
                gemini_url = f"{base_url}/models/{model_name}:generateContent?key={api_key}"
                print(f"[DEBUG] Gemini API 시도: {model_name} @ {base_url[:50]}...")

                try:
                    response = requests.post(
                        gemini_url,
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )

                    if response.status_code == 200:
                        print(f"[DEBUG] 성공: {model_name}")
                        break
                    else:
                        last_error = f"{response.status_code} - {response.text[:200]}"
                        print(f"[WARN] {model_name} 실패: {last_error}")
                        response = None
                except Exception as e:
                    last_error = str(e)
                    print(f"[WARN] {model_name} 예외: {last_error}")
                    response = None

            if response is None or response.status_code != 200:
                print(f"[ERROR] 모든 Gemini API 엔드포인트 실패: {last_error}")
                raise ValueError(f"Gemini API error: {last_error}")

            result = response.json()
            response_text = result['candidates'][0]['content']['parts'][0]['text']
            print("[DEBUG] Gemini Vision API 응답 수신 완료")
            
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            elif response_text.startswith('```'):
                response_text = response_text[3:]
                
            response_text = response_text.strip()
            
            print(f"[DEBUG] JSON 파싱 전: {response_text[:200]}...")
            ai_result = json.loads(response_text)
            print(f"[DEBUG] AI 분석 결과: {ai_result}")

            # item_name을 category로도 저장 (하위 호환성)
            if 'item_name' in ai_result and 'category' not in ai_result:
                ai_result['category'] = ai_result['item_name']
            
            # 색상 정보를 표준 형식으로 변환
            colors = []
            if ai_result.get('primary_color'):
                primary_color_name = ai_result['primary_color']
                # AI가 한글로 응답하므로 그대로 사용
                colors.append({
                    'name': 'primary',
                    'korean_name': primary_color_name,  # 한글 색상명 (AI가 직접 한글로 제공)
                    'hex': self._color_name_to_hex(primary_color_name),  # 매칭용
                    'rgb': (128, 128, 128),
                    'percentage': 80.0
                })

            # 보조 색상 (있을 때만 추가, 최대 1개만)
            secondary_colors = ai_result.get('secondary_colors', [])
            if secondary_colors:  # 빈 배열이 아닐 때만
                # 첫 번째 색상만 사용 (AI가 너무 많이 추가하는 경향이 있음)
                for idx, sec_color in enumerate(secondary_colors[:1]):  # 최대 1개만!
                    if sec_color:  # 빈 문자열 체크
                        colors.append({
                            'name': f'secondary_{idx}',
                            'korean_name': sec_color,  # 한글 색상명 (AI가 직접 한글로 제공)
                            'hex': self._color_name_to_hex(sec_color),
                            'rgb': (100, 100, 100),
                            'percentage': 10.0
                        })
            
            print("[DEBUG] AI 분석 성공!")
            return {
                'success': True,
                'colors': colors,
                'dominant_color': colors[0] if colors else None,
                'ai_analysis': ai_result,
                'method': 'gemini_ai'
            }
            
        except Exception as e:
            error_str = str(e)
            print(f"[ERROR] AI 분석 실패: {type(e).__name__}: {error_str}")
            import traceback
            traceback.print_exc()

            # API 할당량 초과 에러 확인
            if '429' in error_str or 'quota' in error_str.lower() or 'rate' in error_str.lower():
                print("[ERROR] Gemini API 할당량 초과")
                return {
                    'success': False,
                    'error': 'API 할당량 초과',
                    'error_type': 'quota_exceeded',
                    'message': 'AI 분석 서비스가 일시적으로 제한되었습니다. 잠시 후 다시 시도해주세요.',
                    'colors': []
                }

            # 기타 에러도 그대로 반환 (Pillow fallback 제거)
            return {
                'success': False,
                'error': error_str,
                'error_type': 'ai_analysis_failed',
                'message': f'AI 분석 실패: {error_str}',
                'colors': []
            }
    
    def _english_to_korean_color(self, english_name):
        """영문 색상명을 한글로 변환"""
        english_lower = english_name.lower()

        english_to_korean = {
            'red': '빨간색',
            'orange': '주황색',
            'yellow': '노란색',
            'green': '초록색',
            'lightgreen': '연두색',
            'blue': '파란색',
            'skyblue': '하늘색',
            'navy': '남색',
            'purple': '보라색',
            'pink': '분홍색',
            'brown': '갈색',
            'beige': '베이지색',
            'gray': '회색',
            'grey': '회색',
            'black': '검은색',
            'white': '흰색',
            'gold': '금색',
            'silver': '은색',
            'tan': '베이지색',
            'cream': '크림색'
        }

        return english_to_korean.get(english_lower, english_name)

    def _color_name_to_hex(self, color_name):
        """색상 이름을 HEX로 변환 (대략적)"""
        color_name_lower = color_name.lower()
        
        color_map = {
            # 기본 색상
            '빨간색': '#FF0000', '빨강': '#FF0000', '레드': '#FF0000', '적색': '#FF0000',
            '주황색': '#FFA500', '오렌지': '#FFA500', '주황': '#FFA500',
            '노란색': '#FFD700', '노랑': '#FFD700', '옐로우': '#FFD700', '황색': '#FFD700',
            '귤색': '#FF8C00', '밝은 귤색': '#FFA54F', '진한 주황색': '#FF8C00',
            '초록색': '#00FF00', '초록': '#00FF00', '그린': '#00FF00', '녹색': '#00FF00',
            '연두색': '#90EE90', '민트': '#98FF98', '민트 그린': '#98FF98', '연두': '#90EE90',
            '파란색': '#0000FF', '파랑': '#0000FF', '블루': '#0000FF', '청색': '#0000FF',
            '네이비': '#000080', '네이비 블루': '#000080', '남색': '#000080', '감청색': '#000080',
            '하늘색': '#87CEEB', '스카이블루': '#87CEEB', '하늘': '#87CEEB', '연한 파란색': '#ADD8E6',
            '보라색': '#800080', '보라': '#800080', '퍼플': '#800080', '자주색': '#8B008B', '자주': '#8B008B',
            '핑크': '#FFC0CB', '분홍색': '#FFC0CB', '분홍': '#FFC0CB', '연분홍': '#FFB6C1',
            '파스텔 핑크': '#FFB6C1', '연한 분홍색': '#FFB6C1',
            '갈색': '#8B4513', '브라운': '#8B4513', '갈색': '#8B4513', '짙은 갈색': '#654321',
            '베이지': '#F5DEB3', '베이지색': '#F5DEB3', '살구색': '#FFCC99', '살구': '#FFCC99',
            '아이보리': '#FFFFF0', '크림색': '#FFFDD0',
            '회색': '#808080', '그레이': '#808080', '차콜': '#36454F', '은색': '#C0C0C0',
            '차콜 그레이': '#36454F', '짙은 회색': '#696969', '연한 회색': '#D3D3D3',
            '검은색': '#000000', '검정': '#000000', '블랙': '#000000', '흑색': '#000000',
            '흰색': '#FFFFFF', '하양': '#FFFFFF', '화이트': '#FFFFFF', '백색': '#FFFFFF',
            '금색': '#FFD700', '골드': '#FFD700',
            '은색': '#C0C0C0', '실버': '#C0C0C0',
            '산호색': '#FF7F50', '산호': '#FF7F50', '코랄': '#FF7F50',
            '진한 노란색': '#FFA500', '진노란색': '#FFA500', '겨자색': '#FFDB58',
        }
        
        # 정확한 매칭
        for key, hex_val in color_map.items():
            if color_name_lower == key:
                return hex_val
        
        # 부분 매칭 (포함 관계)
        for key, hex_val in color_map.items():
            if key in color_name_lower or color_name_lower in key:
                return hex_val
        
        # 키워드 기반 매칭
        if '노란' in color_name_lower or '노랑' in color_name_lower or '옐로' in color_name_lower or '황' in color_name_lower:
            return '#FFD700'
        elif '초록' in color_name_lower or '녹' in color_name_lower or '그린' in color_name_lower:
            return '#00FF00'
        elif '파란' in color_name_lower or '파랑' in color_name_lower or '청' in color_name_lower or '블루' in color_name_lower:
            return '#0000FF'
        elif '빨간' in color_name_lower or '빨강' in color_name_lower or '적' in color_name_lower or '레드' in color_name_lower:
            return '#FF0000'
        elif '검은' in color_name_lower or '검정' in color_name_lower or '흑' in color_name_lower or '블랙' in color_name_lower:
            return '#000000'
        elif '흰' in color_name_lower or '하얀' in color_name_lower or '백' in color_name_lower or '화이트' in color_name_lower:
            return '#FFFFFF'
        elif '회색' in color_name_lower or '그레이' in color_name_lower or '회' in color_name_lower:
            return '#808080'
        elif '갈색' in color_name_lower or '브라운' in color_name_lower:
            return '#8B4513'
        elif '보라' in color_name_lower or '퍼플' in color_name_lower or '자주' in color_name_lower:
            return '#800080'
        elif '핑크' in color_name_lower or '분홍' in color_name_lower:
            return '#FFC0CB'
        elif '주황' in color_name_lower or '오렌지' in color_name_lower:
            return '#FFA500'
        
        # 기본값 (회색)
        print(f"[WARNING] 알 수 없는 색상: {color_name}, 회색으로 표시")
        return '#808080'
    
    def analyze_image(self, image_path):
        """이미지 분석 메인 함수"""
        try:
            # 이미지 열기
            img = Image.open(image_path)
            
            # RGB로 변환
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 성능을 위해 리사이즈
            img.thumbnail((200, 200))
            
            # 주요 색상 추출
            colors = self.extract_colors(img)
            
            # 색상 이름 매핑
            named_colors = self.map_color_names(colors)
            
            return {
                'success': True,
                'colors': named_colors,
                'dominant_color': named_colors[0] if named_colors else None,
                'method': 'pillow'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'colors': []
            }
    
    def extract_colors(self, img, num_colors=3):
        """이미지에서 주요 색상 추출"""
        # 픽셀 데이터 가져오기
        pixels = list(img.getdata())
        
        # 색상 그룹화 (근사 색상 통합)
        grouped_colors = self.group_similar_colors(pixels)
        
        # 상위 N개 색상 선택
        top_colors = grouped_colors.most_common(num_colors)
        
        results = []
        total_pixels = len(pixels)
        
        for color, count in top_colors:
            percentage = (count / total_pixels) * 100
            
            results.append({
                'rgb': color,
                'hex': self.rgb_to_hex(color),
                'percentage': round(percentage, 1)
            })
        
        return results
    
    def group_similar_colors(self, pixels, tolerance=30):
        """유사한 색상 그룹화"""
        color_groups = Counter()
        
        for pixel in pixels:
            # 가장 가까운 대표 색상 찾기
            grouped_color = self.find_nearest_color_group(pixel, tolerance)
            color_groups[grouped_color] += 1
        
        return color_groups
    
    def find_nearest_color_group(self, rgb, tolerance=30):
        """주어진 RGB와 가장 가까운 색상 그룹 찾기"""
        r, g, b = rgb
        
        # 단순화: 색상을 32단계로 양자화
        step = 32
        r = (r // step) * step
        g = (g // step) * step
        b = (b // step) * step
        
        return (r, g, b)
    
    def map_color_names(self, colors):
        """RGB 색상을 한국어 이름으로 매핑"""
        named_colors = []
        
        for color_data in colors:
            rgb = color_data['rgb']
            color_name = self.get_color_name(rgb)
            
            named_colors.append({
                'name': color_name,
                'korean_name': self.color_names.get(color_name, color_name),
                'hex': color_data['hex'],
                'rgb': rgb,
                'percentage': color_data['percentage']
            })
        
        return named_colors
    
    def get_color_name(self, rgb):
        """RGB 값으로 색상 이름 결정"""
        r, g, b = rgb
        
        # 명도 계산
        brightness = (r + g + b) / 3
        
        # HSV로 변환하여 색상 판단
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h = h * 360  # 각도로 변환
        
        # 1. 무채색 (Black, White, Gray) 판단
        # 채도가 매우 낮으면 무채색
        if s < 0.15:
            if v > 0.85: # 매우 밝음 -> 흰색
                return 'white'
            elif v < 0.2: # 매우 어두움 -> 검은색
                return 'black'
            else:
                return 'gray'
                
        # 2. 유채색이지만 명도가 너무 낮거나 높은 경우 처리
        # 명도가 너무 낮으면 검은색 (기존 60 -> 30으로 완화)
        if brightness < 30:
            return 'black'
            
        # 명도가 너무 높고 채도가 낮으면 흰색
        if brightness > 230 and s < 0.3:
            return 'white'
            
        # 3. 색상(Hue) 기반 판단
        if h < 15 or h >= 345:
            return 'red'
        elif h < 35:
            return 'orange'
        elif h < 70: # 노란색 범위 확장
            return 'yellow'
        elif h < 150: # 초록색 범위 조정
            return 'green'
        elif h < 190: # 하늘색/청록색
            return 'skyblue'
        elif h < 260: # 파란색
            return 'blue'
        elif h < 280: # 남색/보라
            return 'navy'
        elif h < 320: # 보라
            return 'purple'
        elif h < 345: # 핑크
            return 'pink'
        else:
            return 'red'
    
    def rgb_to_hex(self, rgb):
        """RGB를 HEX로 변환"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    
    def calculate_lucky_color_match(self, item_colors, lucky_colors):
        """아이템 색상과 행운색 매칭도 계산"""
        max_match = 30  # 기본 점수
        
        for item_color in item_colors:
            item_name = item_color['korean_name']
            
            for lucky_color in lucky_colors:
                # 정확히 일치
                if item_name == lucky_color:
                    max_match = 100
                    break
                    
                # 유사 색상
                if self.are_similar_colors(item_name, lucky_color):
                    max_match = max(max_match, 70)
        
        return {
            'score': max_match,
            'grade': self.get_match_grade(max_match),
            'message': self.get_match_message(max_match)
        }
    
    def are_similar_colors(self, color1, color2):
        """두 색상이 유사한지 확인"""
        similar_groups = [
            ['빨간색', '주황색', '분홍색'],
            ['파란색', '하늘색', '남색'],
            ['초록색', '연두색'],
            ['노란색', '베이지색', '아이보리색'],
            ['검은색', '회색', '차콜색'],
            ['흰색', '아이보리색', '베이지색'],
            ['보라색', '분홍색']
        ]
        
        for group in similar_groups:
            if color1 in group and color2 in group:
                return True
        return False
    
    def get_match_grade(self, score):
        """매칭 점수에 따른 등급"""
        if score >= 90:
            return 'S'
        elif score >= 70:
            return 'A'
        elif score >= 50:
            return 'B'
        elif score >= 30:
            return 'C'
        else:
            return 'D'
    
    def get_match_message(self, score):
        """매칭 점수에 따른 메시지"""
        if score >= 90:
            return '완벽한 행운의 아이템입니다! 🌟'
        elif score >= 70:
            return '행운을 가져다 줄 좋은 아이템입니다! ✨'
        elif score >= 50:
            return '적당한 행운의 기운이 있습니다. 🍀'
        elif score >= 30:
            return '약간의 행운이 깃들어 있습니다. 💫'
        else:
            return '오늘은 다른 아이템을 시도해보세요. 💭'


# 하위 호환성을 위한 별칭
ImageColorAnalyzer = ItemAnalyzer