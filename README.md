# Lucky Picky - 운세 기반 일상 추천 서비스

운세, 사주, 별자리를 기반으로 개인 맞춤형 일상(OOTD, 메뉴, 아이템)을 추천하는 AI 기반 웹 서비스입니다.

**Live Demo**: https://frontend-wheat-three-93.vercel.app/

## 핵심 기능

- **AI 운세 계산**: OpenAI (GMS) 기반 사주, 별자리, MBTI 종합 분석
- **일간/주간/월간 운세**: 기간별 운세 확인 및 캐싱
- **MBTI 맞춤 톤**: 16가지 MBTI 유형별 운세 멘트 스타일 적용
- **퍼스널컬러 기반 행운색**: 봄웜/여름쿨/가을웜/겨울쿨 유형별 색상 추천
- **OOTD 추천**: 날씨와 운세를 고려한 맞춤형 코디 제안
- **메뉴 추천**: 운세에 맞는 음식 추천
- **아이템 색상 분석**: AI 이미지 분석으로 행운색 매칭도 계산
- **FastText 아이템 유사도**: 행운 아이템과 사용자 아이템 간 의미적 유사도 분석

## 외부 API 서비스

| 기능 | API | 모델/버전 | 용도 |
|------|-----|----------|------|
| 운세 텍스트 생성 | OpenAI (GMS) | `gpt-4o-mini` | 운세 상세 텍스트 AI 생성 |
| 운세 요약 | OpenAI (GMS) | `gpt-5-nano` | 종합운 한줄 요약 |
| 아이템 색상 분석 | Google Gemini | `gemini-2.5-flash` | 이미지에서 색상/카테고리 추출 |
| 날씨 정보 | 기상청 단기예보 | VilageFcstInfoService 2.0 | OOTD 추천용 기온/날씨 |
| 위치 → 주소 변환 | Kakao 로컬 | coord2address | 위경도를 한글 주소로 변환 |

## 빠른 시작

```bash
# 저장소 클론
git clone https://github.com/hsjangjang/fortunepjt.git
cd fortunepjt

# Backend 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend 설정
cd frontend
npm install
cd ..

# 환경 변수 설정 (.env 파일)
GEMINI_API_KEY=your_gemini_api_key          # Google Gemini (아이템 분석)
GMS_API_KEY=your_gms_api_key                # GMS OpenAI (운세 텍스트)
KMA_API_KEY=your_kma_api_key                # 기상청 API
KAKAO_REST_API_KEY=your_kakao_api_key       # 카카오 로컬 API
SECRET_KEY=your_django_secret_key

# DB 초기화
python manage.py migrate

# 서버 실행
python manage.py runserver  # Django API (localhost:8000)
cd frontend && npm run dev  # Vue 개발 서버 (localhost:5173)
```

## 기술 스택

| Backend | Frontend |
|---------|----------|
| Django 5.2 + DRF | Vue 3 (Composition API) |
| Google Gemini AI | Vite + Pinia |
| OpenCV | Bootstrap 5 |
| PostgreSQL (배포) / SQLite (개발) | Axios |

## API 엔드포인트

```
# 인증
POST /api/auth/login/              # 로그인
POST /api/auth/register/           # 회원가입
GET  /api/auth/profile/            # 프로필 조회

# 운세
POST /api/fortune/calculate/       # 운세 계산 (비회원)
GET  /api/fortune/today/           # 오늘의 운세 (회원)
GET  /api/fortune/weekly/          # 이번 주 운세
GET  /api/fortune/monthly/         # 이번 달 운세

# 추천
GET  /api/recommendations/ootd/    # OOTD 추천
GET  /api/recommendations/menu/    # 메뉴 추천

# 아이템
GET  /api/items/                   # 아이템 목록
POST /api/items/                   # 아이템 등록 (이미지 분석)
GET  /api/items/<id>/check/        # 아이템 행운 점수 확인
```

## 프로젝트 구조

```
fortunepjt/
│
├── config/                  # Django 프로젝트 설정
│   ├── settings.py          # 환경 설정 (DB, API 키 등)
│   ├── urls.py              # URL 라우팅
│   └── wsgi.py              # WSGI 설정
│
├── fortune/                 # 운세 앱 (핵심 기능)
│   ├── api_views.py         # REST API 뷰
│   ├── services.py          # 운세 계산 비즈니스 로직
│   ├── saju_calculator.py   # 사주/오행 계산
│   ├── lunar_converter.py   # 음력 변환
│   ├── models.py            # 운세 캐시 모델
│   ├── constants/           # 상수 모듈
│   │   ├── colors.py        # 색상, 퍼스널컬러 팔레트
│   │   ├── items.py         # 행운 아이템 목록
│   │   └── templates.py     # 운세 텍스트 템플릿
│   └── management/commands/ # 관리 명령어
│
├── items/                   # 아이템 앱
│   ├── api_views.py         # 아이템 CRUD API
│   ├── item_analyzer.py     # AI 색상 분석 (Gemini)
│   └── models.py            # UserItem 모델
│
├── recommendations/         # 추천 앱
│   └── api_views.py         # OOTD, 메뉴 추천 API
│
├── users/                   # 사용자 앱
│   ├── api_views.py         # 인증, 프로필 API
│   ├── models.py            # 커스텀 User 모델
│   └── serializers.py       # DRF 시리얼라이저
│
├── core/                    # 공통 유틸리티
│
├── scripts/                 # 유틸리티 스크립트
│   └── generate_similarity_matrix.py  # FastText 유사도 생성
│
├── frontend/                # Vue 3 SPA
│   ├── src/
│   │   ├── views/           # 페이지 컴포넌트
│   │   │   ├── fortune/     # 운세 관련 (Fortune.vue, Loading.vue)
│   │   │   ├── items/       # 아이템 관련 (List.vue, Detail.vue)
│   │   │   ├── auth/        # 인증 (Login.vue, Register.vue)
│   │   │   └── recommendations/  # 추천 (OOTD.vue, Menu.vue)
│   │   ├── stores/          # Pinia 상태 관리
│   │   │   ├── auth.js      # 인증 스토어
│   │   │   └── fortune.js   # 운세 스토어
│   │   ├── utils/           # 유틸리티
│   │   │   ├── colors.js    # 색상 매핑
│   │   │   └── itemSimilarity.js  # FastText 유사도
│   │   ├── data/            # 정적 데이터
│   │   │   └── itemSimilarity.json  # 유사도 매트릭스
│   │   ├── api/             # API 클라이언트
│   │   ├── router/          # Vue Router 설정
│   │   └── assets/          # 이미지 리소스
│   │       ├── images/food/       # 음식 이미지
│   │       ├── images/ootd/       # OOTD 이미지
│   │       └── images/lucky_items/ # 행운 아이템 이미지
│   └── package.json
│
├── .ebextensions/           # AWS Elastic Beanstalk 설정
├── .platform/               # EB 플랫폼 훅
├── Procfile                 # gunicorn 실행 설정
│
├── *.json                   # 데이터 파일 (food, ootd)
├── requirements.txt         # Python 의존성
├── manage.py                # Django 관리 스크립트
├── UPDATE.md                # 업데이트 내역
└── README.md                # 프로젝트 문서
```

## 배포

- **Frontend**: Vercel (자동 배포)
- **Backend**: AWS Elastic Beanstalk
- **Database**: AWS RDS (PostgreSQL)
- **Storage**: AWS S3 (사용자 아이템 이미지)

## 팀

| 이름 | 역할 |
|------|------|
| 장하선 | Backend (운세 API, 사주/오행 계산, LLM 프롬프팅, 아이템 분석, AWS 배포), Frontend (행운 점수 계산, 상태 관리, FastText 유사도) |
| 이수진 | Frontend UI/UX (운세, 메뉴, 아이템 페이지), Backend (아이템 색상 분석), 음식 이미지 리소스 |
| 김유림 | Backend (OOTD/메뉴 추천, 성별별 추천 로직), Frontend (인증 UI, 라우터 가드), OOTD/행운아이템 이미지 리소스 |

- **GitHub**: https://github.com/hsjangjang/fortunepjt

---

**Made with SSAFY 14th 대전 2반 공트리오**
