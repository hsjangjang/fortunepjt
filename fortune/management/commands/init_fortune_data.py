"""
운세 서비스 초기 데이터 생성 명령어
사용법: python manage.py init_fortune_data
"""
from django.core.management.base import BaseCommand
from fortune.models import MBTISpeechTemplate, ColorMaster


class Command(BaseCommand):
    help = '운세 서비스에 필요한 초기 데이터(MBTI 말투 템플릿, 색상 마스터)를 생성합니다.'

    def handle(self, *args, **options):
        self.stdout.write('운세 초기 데이터 생성을 시작합니다...\n')

        # MBTI 말투 템플릿 생성
        self.create_mbti_templates()

        # 색상 마스터 생성
        self.create_color_master()

        self.stdout.write(self.style.SUCCESS('\n모든 초기 데이터 생성이 완료되었습니다!'))

    def create_mbti_templates(self):
        """MBTI별 말투 템플릿 생성"""
        self.stdout.write('MBTI 말투 템플릿 생성 중...')

        # MBTI 유형별 특성에 맞는 말투 템플릿
        mbti_templates = {
            # 분석형 (NT)
            'INTJ': {
                'greeting': '오늘의 운세를 논리적으로 분석해 드릴게요.',
                'fortune_good': '계획했던 일들이 효율적으로 진행될 기운이에요. 전략적 사고가 빛을 발할 거예요.',
                'fortune_bad': '예상치 못한 변수가 생길 수 있어요. 대안을 미리 준비해두면 좋겠네요.',
                'recommendation': '오늘은 장기적 목표를 재점검하기 좋은 날이에요.',
                'encouragement': '당신의 통찰력을 믿으세요. 큰 그림을 보는 능력이 있잖아요.',
                'advice': '완벽주의를 조금 내려놓고, 과정도 즐겨보세요.',
            },
            'INTP': {
                'greeting': '흥미로운 운세 분석이 기다리고 있어요.',
                'fortune_good': '새로운 아이디어가 샘솟는 날이에요. 창의적 문제해결이 가능해요.',
                'fortune_bad': '현실적인 부분에서 약간의 어려움이 있을 수 있어요. 실행력에 집중해보세요.',
                'recommendation': '호기심을 따라가보세요. 예상치 못한 발견이 있을 거예요.',
                'encouragement': '당신의 독특한 시각이 세상을 더 풍요롭게 해요.',
                'advice': '생각만 하지 말고, 작은 것부터 실행해보는 건 어떨까요?',
            },
            'ENTJ': {
                'greeting': '리더십을 발휘할 준비가 되셨나요?',
                'fortune_good': '목표 달성을 향해 강력하게 전진할 수 있는 날이에요. 주도권을 잡으세요!',
                'fortune_bad': '주변 사람들의 의견에도 귀 기울여야 할 때예요. 독단은 피해주세요.',
                'recommendation': '팀원들과 비전을 공유하면 시너지가 날 거예요.',
                'encouragement': '당신의 결단력이 팀을 성공으로 이끌어요.',
                'advice': '때로는 한 발 물러서서 다른 사람에게 기회를 주는 것도 리더십이에요.',
            },
            'ENTP': {
                'greeting': '오늘은 또 어떤 흥미로운 일이 펼쳐질까요?',
                'fortune_good': '창의적 에너지가 넘치는 날! 새로운 프로젝트를 시작하기 좋아요.',
                'fortune_bad': '시작한 일을 끝까지 마무리하는 데 집중이 필요해요.',
                'recommendation': '토론이나 브레인스토밍에 참여해보세요. 빛나는 아이디어가 나올 거예요.',
                'encouragement': '당신의 재치와 유연한 사고가 문제를 해결해요.',
                'advice': '여러 가지를 동시에 하기보다 우선순위를 정해보세요.',
            },

            # 외교형 (NF)
            'INFJ': {
                'greeting': '오늘 하루도 의미 있는 시간이 되길 바라요.',
                'fortune_good': '직감이 빛나는 날이에요. 내면의 목소리를 따라가세요.',
                'fortune_bad': '타인의 감정에 너무 몰입하지 않도록 주의하세요. 자신도 돌봐야 해요.',
                'recommendation': '조용한 시간을 갖고 자신을 돌아보세요.',
                'encouragement': '당신의 공감 능력이 누군가에게 큰 위로가 돼요.',
                'advice': '모든 사람을 구하려 하지 않아도 괜찮아요. 당신 자신부터 챙기세요.',
            },
            'INFP': {
                'greeting': '오늘도 당신만의 아름다운 세계를 펼쳐보세요.',
                'fortune_good': '감성과 창의성이 조화롭게 발휘되는 날이에요. 예술적 영감이 찾아올 거예요.',
                'fortune_bad': '현실과 이상 사이에서 갈등이 있을 수 있어요. 작은 것부터 실천해보세요.',
                'recommendation': '글쓰기나 음악 감상으로 마음을 표현해보세요.',
                'encouragement': '당신의 순수한 마음이 세상을 더 따뜻하게 해요.',
                'advice': '꿈도 좋지만, 현실에서 작은 행동을 시작해보는 건 어떨까요?',
            },
            'ENFJ': {
                'greeting': '오늘도 주변 사람들에게 좋은 영향력을 줄 준비가 되셨나요?',
                'fortune_good': '리더십과 따뜻함이 빛나는 날! 주변 사람들과 좋은 관계를 맺을 수 있어요.',
                'fortune_bad': '남을 돕느라 자신을 소홀히 하지 않도록 주의하세요.',
                'recommendation': '멘토링이나 상담 역할을 해보세요. 보람을 느낄 거예요.',
                'encouragement': '당신의 격려 한마디가 누군가의 인생을 바꿀 수 있어요.',
                'advice': '가끔은 자신만의 시간도 필요해요. 혼자만의 충전 시간을 가져보세요.',
            },
            'ENFP': {
                'greeting': '오늘은 어떤 신나는 일이 기다리고 있을까요?',
                'fortune_good': '열정과 에너지가 넘치는 날! 새로운 사람들과의 만남도 좋아요.',
                'fortune_bad': '산만해지기 쉬운 날이에요. 한 가지에 집중하는 연습을 해보세요.',
                'recommendation': '새로운 취미나 활동에 도전해보세요!',
                'encouragement': '당신의 긍정적 에너지가 주변을 밝게 해요.',
                'advice': '약속은 신중하게, 한 번 한 약속은 꼭 지켜주세요.',
            },

            # 관리자형 (SJ)
            'ISTJ': {
                'greeting': '오늘도 계획대로 차근차근 진행해봐요.',
                'fortune_good': '꾸준함이 빛을 발하는 날이에요. 맡은 일을 완벽하게 마무리할 수 있어요.',
                'fortune_bad': '예상치 못한 변화에 유연하게 대처해야 할 수 있어요.',
                'recommendation': '중요한 서류 정리나 계획 수립을 해보세요.',
                'encouragement': '당신의 책임감과 신뢰성은 정말 대단해요.',
                'advice': '가끔은 계획에서 벗어나 즉흥적인 것도 즐겨보세요.',
            },
            'ISFJ': {
                'greeting': '오늘도 따뜻한 마음으로 하루를 시작해보세요.',
                'fortune_good': '배려와 헌신이 인정받는 날이에요. 주변의 감사 인사를 받을 거예요.',
                'fortune_bad': '자신의 필요도 챙기세요. 남을 돕는 것만큼 중요해요.',
                'recommendation': '소중한 사람에게 작은 선물이나 따뜻한 말을 건네보세요.',
                'encouragement': '당신의 세심한 배려가 많은 사람을 행복하게 해요.',
                'advice': '거절하는 것도 괜찮아요. 모든 부탁을 들어줄 필요 없어요.',
            },
            'ESTJ': {
                'greeting': '효율적인 하루를 보낼 준비 되셨나요?',
                'fortune_good': '조직력이 빛나는 날! 프로젝트를 성공적으로 이끌 수 있어요.',
                'fortune_bad': '다른 사람의 방식도 존중해주세요. 내 방식만이 정답은 아니에요.',
                'recommendation': '팀을 이끌거나 중요한 결정을 내리기 좋은 날이에요.',
                'encouragement': '당신의 추진력이 팀의 성과를 만들어내요.',
                'advice': '규칙도 중요하지만, 상황에 따른 유연성도 필요해요.',
            },
            'ESFJ': {
                'greeting': '오늘도 주변 사람들과 따뜻한 하루 보내세요!',
                'fortune_good': '사교성이 빛나는 날! 모임이나 행사에서 인기를 끌 거예요.',
                'fortune_bad': '남의 시선을 너무 의식하지 마세요. 자신의 기준이 중요해요.',
                'recommendation': '친구들과 함께하는 시간을 가져보세요.',
                'encouragement': '당신의 친화력이 모든 사람을 편안하게 해요.',
                'advice': '갈등 상황에서 중립을 지키는 것도 방법이에요.',
            },

            # 탐험가형 (SP)
            'ISTP': {
                'greeting': '오늘은 어떤 것을 분석하고 만들어볼까요?',
                'fortune_good': '문제 해결 능력이 빛나는 날! 기술적인 일에서 성과가 있을 거예요.',
                'fortune_bad': '감정 표현이 필요한 상황이 올 수 있어요. 마음을 열어보세요.',
                'recommendation': '손으로 하는 작업이나 새로운 기술을 배워보세요.',
                'encouragement': '당신의 냉철한 분석력이 문제를 해결해요.',
                'advice': '가끔은 논리보다 감정도 표현해보세요.',
            },
            'ISFP': {
                'greeting': '오늘도 당신만의 감성으로 세상을 바라봐요.',
                'fortune_good': '예술적 감각이 빛나는 날! 창작 활동에 좋은 결과가 있을 거예요.',
                'fortune_bad': '결정을 미루지 말고 용기를 내어 선택해보세요.',
                'recommendation': '자연 속에서 시간을 보내거나 예술 활동을 해보세요.',
                'encouragement': '당신의 섬세한 감성이 특별한 작품을 만들어요.',
                'advice': '자신의 의견도 당당하게 말해보세요.',
            },
            'ESTP': {
                'greeting': '액션 가득한 하루가 기다리고 있어요!',
                'fortune_good': '순발력이 빛나는 날! 즉흥적인 기회를 잡을 수 있어요.',
                'fortune_bad': '충동적인 결정은 피하세요. 잠깐 멈추고 생각해보세요.',
                'recommendation': '스포츠나 야외 활동을 즐겨보세요.',
                'encouragement': '당신의 대담함이 새로운 기회를 만들어요.',
                'advice': '장기적인 결과도 생각해보는 습관을 들여보세요.',
            },
            'ESFP': {
                'greeting': '오늘도 즐거운 하루가 될 거예요!',
                'fortune_good': '사교성과 즐거움이 넘치는 날! 파티나 모임의 주인공이 될 거예요.',
                'fortune_bad': '진지한 일에도 집중이 필요해요. 놀기만 할 순 없잖아요.',
                'recommendation': '친구들과 함께 즐거운 활동을 계획해보세요.',
                'encouragement': '당신의 밝은 에너지가 모두를 행복하게 해요.',
                'advice': '미래를 위한 계획도 조금씩 세워보세요.',
            },
        }

        created_count = 0
        updated_count = 0

        for mbti_type, templates in mbti_templates.items():
            for category, template_text in templates.items():
                obj, created = MBTISpeechTemplate.objects.update_or_create(
                    mbti_type=mbti_type,
                    category=category,
                    defaults={
                        'template_text': template_text,
                        'tone': 'friendly'
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'  MBTI 말투 템플릿: {created_count}개 생성, {updated_count}개 업데이트')
        )

    def create_color_master(self):
        """색상 마스터 데이터 생성"""
        self.stdout.write('색상 마스터 데이터 생성 중...')

        colors = [
            # 빨강 계열
            {'code': '#FF0000', 'name': '빨강', 'category': '빨강', 'r': 255, 'g': 0, 'b': 0,
             'meaning': '열정, 에너지, 사랑, 용기', 'keywords': ['열정', '활력', '자신감', '리더십']},
            {'code': '#DC143C', 'name': '크림슨', 'category': '빨강', 'r': 220, 'g': 20, 'b': 60,
             'meaning': '강렬함, 결단력', 'keywords': ['결단', '의지', '승부욕']},
            {'code': '#FF6B6B', 'name': '코랄 레드', 'category': '빨강', 'r': 255, 'g': 107, 'b': 107,
             'meaning': '따뜻함, 친근함', 'keywords': ['친근', '온기', '사랑']},

            # 주황 계열
            {'code': '#FF8C00', 'name': '주황', 'category': '주황', 'r': 255, 'g': 140, 'b': 0,
             'meaning': '창의성, 활력, 따뜻함', 'keywords': ['창의성', '활력', '사교성', '낙관']},
            {'code': '#FF7F50', 'name': '코랄', 'category': '주황', 'r': 255, 'g': 127, 'b': 80,
             'meaning': '생기, 친화력', 'keywords': ['친화', '생기', '매력']},
            {'code': '#FFA500', 'name': '오렌지', 'category': '주황', 'r': 255, 'g': 165, 'b': 0,
             'meaning': '즐거움, 성공', 'keywords': ['성공', '즐거움', '풍요']},

            # 노랑 계열
            {'code': '#FFD700', 'name': '금색', 'category': '노랑', 'r': 255, 'g': 215, 'b': 0,
             'meaning': '부, 성공, 지혜', 'keywords': ['재물', '성공', '명예', '지혜']},
            {'code': '#FFFF00', 'name': '노랑', 'category': '노랑', 'r': 255, 'g': 255, 'b': 0,
             'meaning': '행복, 희망, 밝음', 'keywords': ['행복', '희망', '밝음', '지적호기심']},
            {'code': '#F0E68C', 'name': '카키', 'category': '노랑', 'r': 240, 'g': 230, 'b': 140,
             'meaning': '안정, 자연', 'keywords': ['안정', '평화', '자연']},

            # 초록 계열
            {'code': '#00FF00', 'name': '초록', 'category': '초록', 'r': 0, 'g': 255, 'b': 0,
             'meaning': '성장, 건강, 조화', 'keywords': ['성장', '건강', '조화', '새로운시작']},
            {'code': '#228B22', 'name': '포레스트 그린', 'category': '초록', 'r': 34, 'g': 139, 'b': 34,
             'meaning': '안정, 신뢰', 'keywords': ['안정', '신뢰', '자연']},
            {'code': '#98FB98', 'name': '연두', 'category': '초록', 'r': 152, 'g': 251, 'b': 152,
             'meaning': '새로움, 청춘', 'keywords': ['새로움', '청춘', '희망']},
            {'code': '#2E8B57', 'name': '시 그린', 'category': '초록', 'r': 46, 'g': 139, 'b': 87,
             'meaning': '치유, 평온', 'keywords': ['치유', '평온', '회복']},

            # 파랑 계열
            {'code': '#0000FF', 'name': '파랑', 'category': '파랑', 'r': 0, 'g': 0, 'b': 255,
             'meaning': '신뢰, 안정, 지성', 'keywords': ['신뢰', '안정', '지성', '충성']},
            {'code': '#4169E1', 'name': '로열 블루', 'category': '파랑', 'r': 65, 'g': 105, 'b': 225,
             'meaning': '권위, 명예', 'keywords': ['권위', '명예', '품격']},
            {'code': '#87CEEB', 'name': '스카이 블루', 'category': '파랑', 'r': 135, 'g': 206, 'b': 235,
             'meaning': '자유, 평화', 'keywords': ['자유', '평화', '청명']},
            {'code': '#000080', 'name': '네이비', 'category': '파랑', 'r': 0, 'g': 0, 'b': 128,
             'meaning': '진중함, 신뢰', 'keywords': ['진중', '신뢰', '전문성']},
            {'code': '#00CED1', 'name': '다크 터콰이즈', 'category': '파랑', 'r': 0, 'g': 206, 'b': 209,
             'meaning': '창의성, 소통', 'keywords': ['소통', '창의', '영감']},

            # 보라 계열
            {'code': '#800080', 'name': '보라', 'category': '보라', 'r': 128, 'g': 0, 'b': 128,
             'meaning': '고귀함, 신비, 창의성', 'keywords': ['고귀', '신비', '창의성', '영성']},
            {'code': '#9370DB', 'name': '미디엄 퍼플', 'category': '보라', 'r': 147, 'g': 112, 'b': 219,
             'meaning': '상상력, 꿈', 'keywords': ['상상력', '꿈', '로맨스']},
            {'code': '#E6E6FA', 'name': '라벤더', 'category': '보라', 'r': 230, 'g': 230, 'b': 250,
             'meaning': '우아함, 평온', 'keywords': ['우아', '평온', '휴식']},
            {'code': '#8B008B', 'name': '다크 마젠타', 'category': '보라', 'r': 139, 'g': 0, 'b': 139,
             'meaning': '변화, 혁신', 'keywords': ['변화', '혁신', '독창성']},

            # 분홍 계열
            {'code': '#FFC0CB', 'name': '핑크', 'category': '분홍', 'r': 255, 'g': 192, 'b': 203,
             'meaning': '사랑, 로맨스, 부드러움', 'keywords': ['사랑', '로맨스', '부드러움', '애정']},
            {'code': '#FF69B4', 'name': '핫 핑크', 'category': '분홍', 'r': 255, 'g': 105, 'b': 180,
             'meaning': '열정적 사랑, 매력', 'keywords': ['매력', '열정', '자기애']},
            {'code': '#FFB6C1', 'name': '라이트 핑크', 'category': '분홍', 'r': 255, 'g': 182, 'b': 193,
             'meaning': '순수, 다정함', 'keywords': ['순수', '다정', '온화']},

            # 갈색 계열
            {'code': '#8B4513', 'name': '갈색', 'category': '갈색', 'r': 139, 'g': 69, 'b': 19,
             'meaning': '안정, 신뢰, 대지', 'keywords': ['안정', '신뢰', '실용', '근면']},
            {'code': '#D2691E', 'name': '초콜릿', 'category': '갈색', 'r': 210, 'g': 105, 'b': 30,
             'meaning': '따뜻함, 편안함', 'keywords': ['따뜻함', '편안', '포근']},
            {'code': '#F5DEB3', 'name': '밀색', 'category': '갈색', 'r': 245, 'g': 222, 'b': 179,
             'meaning': '자연, 순수', 'keywords': ['자연', '순수', '소박']},

            # 무채색
            {'code': '#FFFFFF', 'name': '흰색', 'category': '무채색', 'r': 255, 'g': 255, 'b': 255,
             'meaning': '순수, 깨끗함, 새로운 시작', 'keywords': ['순수', '깨끗함', '새출발', '진실']},
            {'code': '#000000', 'name': '검정', 'category': '무채색', 'r': 0, 'g': 0, 'b': 0,
             'meaning': '세련됨, 권위, 신비', 'keywords': ['세련', '권위', '카리스마', '보호']},
            {'code': '#808080', 'name': '회색', 'category': '무채색', 'r': 128, 'g': 128, 'b': 128,
             'meaning': '중립, 균형, 절제', 'keywords': ['중립', '균형', '절제', '지혜']},
            {'code': '#C0C0C0', 'name': '실버', 'category': '무채색', 'r': 192, 'g': 192, 'b': 192,
             'meaning': '현대적, 세련됨', 'keywords': ['현대', '세련', '기술']},

            # 베이지/크림 계열
            {'code': '#F5F5DC', 'name': '베이지', 'category': '베이지', 'r': 245, 'g': 245, 'b': 220,
             'meaning': '따뜻함, 편안함, 안정', 'keywords': ['따뜻함', '편안', '안정', '포용']},
            {'code': '#FFFDD0', 'name': '크림', 'category': '베이지', 'r': 255, 'g': 253, 'b': 208,
             'meaning': '부드러움, 우아함', 'keywords': ['부드러움', '우아', '고급']},
            {'code': '#FAEBD7', 'name': '앤틱 화이트', 'category': '베이지', 'r': 250, 'g': 235, 'b': 215,
             'meaning': '클래식, 품격', 'keywords': ['클래식', '품격', '전통']},
        ]

        created_count = 0
        updated_count = 0

        for color in colors:
            obj, created = ColorMaster.objects.update_or_create(
                color_code=color['code'],
                defaults={
                    'color_name': color['name'],
                    'color_category': color['category'],
                    'rgb_r': color['r'],
                    'rgb_g': color['g'],
                    'rgb_b': color['b'],
                    'meaning': color['meaning'],
                    'fortune_keywords': color['keywords']
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'  색상 마스터: {created_count}개 생성, {updated_count}개 업데이트')
        )
