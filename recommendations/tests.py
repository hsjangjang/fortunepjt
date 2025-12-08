from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from recommendations.views import load_food_data, get_color_mapping, get_food_by_color, menu_recommendation

class MenuRecommendationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_load_food_data(self):
        """food.json 파일이 정상적으로 로드되는지 테스트"""
        data = load_food_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        # 첫 번째 아이템이 예상되는 키를 가지고 있는지 확인
        first_item = data[0]
        self.assertIn('name_ko', first_item)
        self.assertIn('color_category', first_item)

    def test_color_mapping(self):
        """색상 매핑이 올바르게 작동하는지 테스트"""
        mapping = get_color_mapping()
        self.assertIn('빨간색', mapping)
        self.assertIn('red', mapping['빨간색'])
        self.assertIn('red/yellow', mapping['빨간색']) # 확장된 매핑 확인

    def test_get_food_by_color(self):
        """행운색 기반 음식 필터링 테스트"""
        # 빨간색 음식 테스트
        red_foods = get_food_by_color('빨간색')
        self.assertGreater(len(red_foods), 0)
        for food in red_foods:
            # food['color_category']에 'red' 관련 키워드가 포함되어 있어야 함
            # 또는 매핑된 키워드 중 하나가 포함되어야 함
            color_cat = food['color_category'].lower()
            is_match = any(k in color_cat for k in ['red', 'crimson', 'pink/red'])
            self.assertTrue(is_match, f"Food {food['name_ko']} with color {color_cat} should match '빨간색'")

        # 노란색 음식 테스트
        yellow_foods = get_food_by_color('노란색')
        self.assertGreater(len(yellow_foods), 0)
        
    def test_menu_recommendation_view(self):
        """뷰 함수 테스트"""
        request = self.factory.get('/recommendations/menu/')
        
        # 세션 미들웨어 시뮬레이션
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # 로그인 시뮬레이션 (mock user)
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='testuser', password='password')
        request.user = user
        
        # 세션에 행운 데이터 설정
        request.session['fortune_data'] = {'lucky_colors': ['빨간색']}
        
        response = menu_recommendation(request)
        
        self.assertEqual(response.status_code, 200)
        # context 데이터 확인 (TemplateResponse가 아니라 HttpResponse일 수 있음)
        # render 함수는 HttpResponse를 반환하므로 content를 확인해야 함
        self.assertContains(response, '행운의 빨간색')
