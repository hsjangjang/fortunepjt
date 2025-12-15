"""
아이템 이미지 분석 모듈
- 색상 분석: Pillow + 색상 클러스터링
- AI 분석: Google Gemini Vision API
  - 아이템 이름 자동 감지
  - 관련 태그 생성
  - 운세별 점수 계산 (love, money, work, health, study)
"""
from PIL import Image

from collections import Counter
import colorsys
import json
import os

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
        """Gemini Vision API를 사용한 AI 이미지 분석"""
        print(f"[DEBUG] AI 분석 시작: {image_path}")
        try:
            import google.generativeai as genai
            from django.conf import settings
            
            # API 키 설정
            api_key = settings.GEMINI_API_KEY
            print(f"[DEBUG] API 키 확인: {api_key[:10]}..." if api_key else "[DEBUG] API 키 없음!")
            
            if not api_key:
                raise ValueError("GEMINI_API_KEY not configured")
            
            genai.configure(api_key=api_key)
            print("[DEBUG] Gemini 설정 완료")
            
            # gemini-2.5-flash 모델 사용
            vision_model = 'gemini-2.5-flash'
            print(f"[DEBUG] 사용 모델: {vision_model}")
            model = genai.GenerativeModel(vision_model)
            print("[DEBUG] 모델 초기화 완료")
            
            # 이미지 파일 읽기
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            ]
            
            prompt = """
            이 이미지에 있는 **물체**를 분석해주세요. 배경은 무시하고 주요 물체만 분석하세요.

            다음 정보를 JSON 형식으로 제공해주세요:

            1. item_name: 물체의 구체적인 이름 (한글로, 2-4글자)
               - 예시: '마우스', '향수', '지갑', '키링', '인형', '껌', '사탕', '초콜릿', '이어폰', '목걸이', '반지', '팔찌', '립스틱', '볼펜', '텀블러' 등
               - 구체적인 물건 이름을 사용하세요

            2. primary_color: 물체의 **가장 넓은 면적을 차지하는** 주요 색상 (한글로)
               - **반드시 아래 15가지 중 하나만 선택**:
                 '빨간색', '주황색', '노란색', '초록색', '파란색', '보라색', '분홍색', '갈색', '베이지색', '회색', '검은색', '흰색', '남색', '하늘색', '금색'
               - 배경색이나 작은 로고 색상은 제외하고 물체 자체의 색상만 판단
               - 어두운 색(짙은 네이비, 차콜, 진회색 등)은 '검은색'으로 분류

            3. secondary_colors: 보조 색상 배열
               - **단색 물체(한 가지 색만 보이는 경우)는 반드시 빈 배열 []**
               - 두 가지 이상의 색이 **전체 면적의 20% 이상**을 차지할 때만 추가
               - 로고, 스티칭(박음질), 지퍼, 단추, 장식 등 작은 부분의 색상은 무시
               - 그라데이션, 반사광, 그림자는 별도 색상으로 취급하지 않음
               - **확실하지 않으면 빈 배열 []로 응답**

            4. tags: 해시태그 3개 (아이템 특성과 행운 관련)
               - 첫 번째: 아이템 종류 (예: '지갑', '향수', '키링')
               - 두 번째: **반드시** 아래 5개 운세 중 하나 선택 (필수!):
                 '애정운', '금전운', '직장운', '건강운', '학업운'
               - 세 번째: 아이템 느낌이나 특성 (예: '고급스러움', '심플함', '귀여움', '세련됨')

            5. fortune_scores: 이 아이템이 각 운세를 얼마나 강화해주는지 점수 (0~100)
               - love: 애정운 강화 점수
               - money: 금전운 강화 점수
               - work: 직장운 강화 점수
               - health: 건강운 강화 점수
               - study: 학업운 강화 점수
               - 아이템 특성에 따라 판단:
                 * 지갑, 돈, 금고 → money 높음
                 * 향수, 반지, 꽃 → love 높음
                 * 마우스, 명함, 볼펜 → work 높음
                 * 운동용품, 물병, 비타민 → health 높음
                 * 노트, 펜, 책 → study 높음

            **중요**:
            - 반드시 유효한 JSON 형식으로만 응답
            - 모든 값은 한글로 작성 (fortune_scores의 키는 영문)
            - 마크다운 코드 블록(```) 절대 사용 금지
            - 단색 물체는 secondary_colors를 빈 배열로!
            - tags의 두 번째 요소는 반드시 '애정운', '금전운', '직장운', '건강운', '학업운' 중 하나!

            예시 1 (검은 지갑):
            {
              "item_name": "지갑",
              "primary_color": "검은색",
              "secondary_colors": [],
              "tags": ["지갑", "금전운", "고급스러움"],
              "fortune_scores": {"love": 20, "money": 95, "work": 50, "health": 10, "study": 15}
            }

            예시 2 (분홍+금색 향수):
            {
              "item_name": "향수",
              "primary_color": "분홍색",
              "secondary_colors": ["금색"],
              "tags": ["향수", "애정운", "화려함"],
              "fortune_scores": {"love": 90, "money": 30, "work": 40, "health": 15, "study": 10}
            }

            예시 3 (검은 마우스):
            {
              "item_name": "마우스",
              "primary_color": "검은색",
              "secondary_colors": [],
              "tags": ["마우스", "직장운", "심플함"],
              "fortune_scores": {"love": 10, "money": 40, "work": 85, "health": 15, "study": 30}
            }
            """
            
            print("[DEBUG] Gemini API 호출 시작")
            response = model.generate_content([prompt, image_parts[0]])
            response.resolve()
            response_text = response.text
            print("[DEBUG] Gemini API 응답 수신 완료")
            
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
                print("[ERROR] Gemini API 할당량 초과 - Pillow fallback 없이 에러 반환")
                return {
                    'success': False,
                    'error': 'API 할당량 초과',
                    'error_type': 'quota_exceeded',
                    'message': 'AI 분석 서비스가 일시적으로 제한되었습니다. 잠시 후 다시 시도해주세요.',
                    'colors': []
                }

            # 기타 에러는 Pillow fallback
            return self.analyze_image(image_path)
    
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
        """색상 이름을 HEX로 변환 (프론트엔드 colorMap과 동기화)"""
        color_name_lower = color_name.lower()

        # 프론트엔드 colors.js의 colorMap과 동일하게 매핑
        color_map = {
            # 검은색 계열
            '검은색': '#1f2937', '검정': '#1f2937', '검정색': '#1f2937', '블랙': '#1f2937', '흑색': '#1f2937',
            # 흰색 계열
            '흰색': '#f3f4f6', '하양': '#f3f4f6', '하얀색': '#f3f4f6', '화이트': '#f3f4f6', '백색': '#f3f4f6',
            # 회색 계열
            '회색': '#6B7280', '그레이': '#6B7280', '그래이': '#6B7280',
            '차콜': '#36454F', '차콜 그레이': '#36454F', '짙은 회색': '#36454F',
            # 빨간색 계열
            '빨간색': '#EF4444', '빨강': '#EF4444', '레드': '#EF4444', '적색': '#EF4444',
            '진한 빨간색': '#B91C1C', '다크레드': '#B91C1C',
            '와인': '#722F37', '버건디': '#800020', '마룬': '#800000',
            '코랄': '#FF7F50', '산호색': '#FF7F50', '산호': '#FF7F50', '살몬': '#FA8072',
            # 분홍색 계열
            '분홍색': '#F472B6', '분홍': '#F472B6', '핑크': '#F472B6',
            '연분홍': '#F472B6', '파스텔 핑크': '#F472B6', '연한 분홍색': '#F472B6',
            # 주황색 계열
            '주황색': '#F59E0B', '주황': '#F59E0B', '오렌지': '#F59E0B',
            '귤색': '#F59E0B', '밝은 귤색': '#F59E0B', '진한 주황색': '#F59E0B',
            # 노란색 계열
            '노란색': '#FCD34D', '노랑': '#FCD34D', '옐로우': '#FCD34D', '황색': '#FCD34D',
            '진한 노란색': '#F59E0B', '진노란색': '#F59E0B', '겨자색': '#FCD34D',
            '금색': '#FFD700', '금': '#FFD700', '골드': '#FFD700', '황금색': '#FFD700',
            # 초록색 계열
            '초록색': '#10B981', '초록': '#10B981', '녹색': '#10B981', '그린': '#10B981',
            '연두색': '#84CC16', '연두': '#84CC16',
            '민트': '#98FF98', '민트색': '#98FF98', '민트 그린': '#98FF98',
            '카키': '#8B8B00', '올리브': '#808000',
            # 파란색 계열
            '파란색': '#3B82F6', '파랑': '#3B82F6', '블루': '#3B82F6', '청색': '#3B82F6',
            '하늘색': '#38BDF8', '스카이블루': '#38BDF8', '하늘': '#38BDF8', '연한 파란색': '#38BDF8',
            '남색': '#1E3A8A', '네이비': '#1E3A8A', '네이비 블루': '#1E3A8A', '감청색': '#1E3A8A',
            '터콰이즈': '#40E0D0', '청록': '#008B8B', '청록색': '#008B8B',
            # 보라색 계열
            '보라색': '#8B5CF6', '보라': '#8B5CF6', '퍼플': '#8B5CF6',
            '자주색': '#8B5CF6', '자주': '#8B5CF6',
            '연보라색': '#DA70D6', '연보라': '#E6E6FA', '라벤더': '#E6E6FA',
            # 갈색 계열
            '갈색': '#92400E', '브라운': '#92400E', '짙은 갈색': '#92400E',
            '베이지': '#E7E5E4', '베이지색': '#E7E5E4',
            '아이보리': '#FFFFF0', '크림색': '#FFFDD0', '살구색': '#FFCC99', '살구': '#FFCC99',
            # 은색
            '은색': '#C0C0C0', '은': '#C0C0C0', '실버': '#C0C0C0',
        }
        
        # 정확한 매칭
        for key, hex_val in color_map.items():
            if color_name_lower == key:
                return hex_val
        
        # 부분 매칭 (포함 관계)
        for key, hex_val in color_map.items():
            if key in color_name_lower or color_name_lower in key:
                return hex_val
        
        # 키워드 기반 매칭 (프론트엔드 colorMap과 동기화된 HEX 값 사용)
        if '노란' in color_name_lower or '노랑' in color_name_lower or '옐로' in color_name_lower:
            return '#FCD34D'
        elif '황' in color_name_lower or '금' in color_name_lower or '골드' in color_name_lower:
            return '#FFD700'
        elif '초록' in color_name_lower or '녹' in color_name_lower or '그린' in color_name_lower:
            return '#10B981'
        elif '하늘' in color_name_lower or '스카이' in color_name_lower:
            return '#38BDF8'
        elif '파란' in color_name_lower or '파랑' in color_name_lower or '블루' in color_name_lower:
            return '#3B82F6'
        elif '남' in color_name_lower or '네이비' in color_name_lower:
            return '#1E3A8A'
        elif '빨간' in color_name_lower or '빨강' in color_name_lower or '적' in color_name_lower or '레드' in color_name_lower:
            return '#EF4444'
        elif '검은' in color_name_lower or '검정' in color_name_lower or '흑' in color_name_lower or '블랙' in color_name_lower:
            return '#1f2937'
        elif '흰' in color_name_lower or '하얀' in color_name_lower or '백' in color_name_lower or '화이트' in color_name_lower:
            return '#f3f4f6'
        elif '회색' in color_name_lower or '그레이' in color_name_lower:
            return '#6B7280'
        elif '갈색' in color_name_lower or '브라운' in color_name_lower:
            return '#92400E'
        elif '보라' in color_name_lower or '퍼플' in color_name_lower or '자주' in color_name_lower:
            return '#8B5CF6'
        elif '핑크' in color_name_lower or '분홍' in color_name_lower:
            return '#F472B6'
        elif '주황' in color_name_lower or '오렌지' in color_name_lower:
            return '#F59E0B'
        elif '베이지' in color_name_lower:
            return '#E7E5E4'

        # 기본값 (회색)
        print(f"[WARNING] 알 수 없는 색상: {color_name}, 회색으로 표시")
        return '#6B7280'
    
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