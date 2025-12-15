# 🔮 Fortune Life - 운세 기반 일상 추천 서비스

운세, 사주, 별자리를 기반으로 개인 맞춤형 일상(OOTD, 메뉴, 아이템)을 추천하는 AI 기반 웹 서비스입니다.

**🌐 Live Demo**: https://frontend-wheat-three-93.vercel.app/

## 🎯 핵심 기능

- 🎨 **AI 운세 계산**: Google Gemini 기반 사주, 별자리, MBTI 종합 분석
- 👔 **OOTD 추천**: 날씨와 운세를 고려한 맞춤형 코디 제안
- 🍽️ **메뉴 추천**: 운세에 맞는 음식 추천
- 📸 **아이템 색상 분석**: AI 이미지 분석으로 행운색 매칭도 계산

## 🔌 외부 API 서비스

| 기능 | API | 모델/버전 | 용도 |
|------|-----|----------|------|
| 운세 텍스트 생성 | OpenAI (GMS) | `gpt-4o-mini` | 운세 상세 텍스트 AI 생성 |
| 운세 요약 | OpenAI (GMS) | `gpt-5-nano` | 종합운 한줄 요약 |
| 아이템 색상 분석 | Google Gemini | `gemini-pro-vision` | 이미지에서 색상/카테고리 추출 |
| 날씨 정보 | 기상청 단기예보 | VilageFcstInfoService 2.0 | OOTD 추천용 기온/날씨 |
| 위치 → 주소 변환 | Kakao 로컬 | coord2address | 위경도를 한글 주소로 변환 |

## 🚀 빠른 시작

```bash
# 저장소 클론
git clone https://github.com/hsjangjang/fortunepjt.git
cd pjt

# Python 가상환경
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Node.js 의존성
npm install

# 환경 변수 설정 (.env 파일)
GEMINI_API_KEY=your_gemini_api_key          # Google Gemini (아이템 분석)
GMS_API_KEY=your_gms_api_key                # GMS OpenAI (운세 텍스트)
KMA_API_KEY=your_kma_api_key                # 기상청 API
KAKAO_REST_API_KEY=your_kakao_api_key       # 카카오 로컬 API
SECRET_KEY=your_django_secret_key

# DB 초기화
python manage.py migrate

# 서버 실행
python manage.py runserver  # Django API
npm run dev                 # Vue 개발 서버
```

## 💻 기술 스택

| Backend | Frontend |
|---------|----------|
| Django 5.2 + DRF | Vue 3 (Composition API) |
| Google Gemini AI | Vite + Pinia |
| OpenCV | Bootstrap 5 |

## 📡 API 엔드포인트

```
POST /api/auth/login/              # 로그인
POST /api/auth/register/           # 회원가입
POST /api/fortune/calculate/       # 운세 계산
GET  /api/fortune/today/           # 오늘의 운세
GET  /api/recommendations/ootd/    # OOTD 추천
GET  /api/recommendations/menu/    # 메뉴 추천
GET  /api/items/                   # 아이템 목록
POST /api/items/                   # 아이템 등록
```

## 🏗️ 프로젝트 구조

```
pjt/
├── config/              # Django 설정
├── fortune/             # 운세 계산 (services.py, api_views.py)
├── recommendations/     # OOTD, 메뉴 추천
├── items/               # 아이템 색상 분석
├── users/               # 사용자 관리
├── frontend/            # Vue 3 SPA
│   └── src/
│       ├── views/       # 페이지 컴포넌트
│       ├── stores/      # Pinia 상태 관리
│       └── api/         # API 클라이언트
└── vite.config.js
```
## 📧 팀

| 이름 | 역할 |
|------|------|
| 장하선 | Backend 개발 (운세 API, 아이템 분석, 배포), Frontend 로직 (행운 점수 계산, 상태 관리) |
| 이수진 | Frontend UI/UX (운세, 메뉴, 아이템 페이지), 이미지 리소스 관리 |
| 김유림 | Backend 추천 로직 (OOTD, 메뉴), Frontend UI, OOTD 이미지 리소스 |

- **GitHub**: https://github.com/hsjangjang/fortunepjt

---

**Made with ❤️ by SSAFY Team**
