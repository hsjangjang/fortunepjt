# 📋 업데이트 내역

## v1.7.0 (25.12.15)

### 장하선
- Backend
  - 주간/월간 운세 생성 프롬프트 수정, API 소진 시 메일 발송, 프롬프팅 개선 (`fortune/services.py`)
  - 이주/이달 운세 API 엔드포인트 추가 (`fortune/api_views.py`)
  - WeeklyFortuneCache, MonthlyFortuneCache 모델 추가 (`fortune/models.py`)
  - 주간/월간 운세 캐시 관리 (`fortune/admin.py`, `fortune/management/commands/`)
- Frontend
  - Today.vue에서 이름 변경, 주간/월간 탭 추가, 오늘 날짜 볼드 처리 (`Fortune.vue`)
  - 로딩 페이지 문구 변경 (`Loading.vue`)
  - 행운 지수 계산 로직 수정 - 색상 + 아이템 유사도 (`ItemCheck.vue`)
  - 행운 지수 바로 표시, UI 수정 (`Detail.vue`)
  - "오늘의 운세" → "운세 확인하기" (`Navbar.vue`)
  - Fortune.vue 라우팅 변경 (`router/index.js`)
  - 주간/월간 운세 스토어 추가 (`fortune.js`)
- Data
  - food.json id 1칸씩 당김
- etc
  - README.md 업데이트 및 UPDATE.md 추가

### 이수진
- Frontend
  - 마파두부, 해물파전, 잔치국수, 어묵탕, 감자탕, 곰탕 이미지 변경 (`assets/images/food/`)
  - menu.vue 데이터와 다른 이미지 삭제 (`Menu.vue`)

### 김유림
- Frontend
  - bottom_corduroy, bottom_fleece, outer_shearling 배경 수정 (`assets/images/ootd/`)

---

## v1.6.0 (25.12.13)

### 김유림
- Backend
  - 성별에 따른 OOTD 추천 로직 (`recommendations/api_views.py`)
- Frontend
  - 비로그인 시 로또 번호 숨김 (`Today.vue`)
- Data
  - 성별별 OOTD 데이터 분리 (`ootd_female.json`, `ootd_male.json`)

---

## v1.5.0 (25.12.12)

### 장하선
- Backend
  - AI HEX→한글 색상명 매핑, 프롬프트 강화 (배경색 인식 방지), Google Cloud Gemini API 직접 연결, 이미지 리사이징 복원 (`items/item_analyzer.py`)
  - 아이템 분석 API 수정 (`items/api_views.py`)
  - Gemini API 설정 추가 (`config/settings.py`)
- Frontend
  - 행운색 점수 반영 로직 재수정 (`colors.js`)
  - 유저 아이템 넘버링 수정 (`Detail.vue`)
  - 행운템 등록 문제 수정 (`ItemCheck.vue`, `Upload.vue`)
  - 음식 사진 추가 (`twigim.png`, `yukgaejang.png`)
- 기타
  - 레거시 파일 및 폴더 정리 (templates/, static/, *.py 등 다수)

### 이수진
- Frontend
  - 음식 이미지 대량 변경 (확장자 jpg→png 포함) (`assets/images/food/`)
  - 버튼 링크 수정 (`Navbar.vue`)
  - 아이템 등록 시 알림창 변경 (`ItemCheck.vue`)

### 김유림
- Backend
  - 음식 & 옷 랜덤 변경 수정 (`recommendations/api_views.py`)

---

## v1.4.0 (25.12.11)

### 장하선
- Backend
  - 운세 생성 API GMS 변경 (GPT-4o-mini), 운세 텍스트 생성 로직 개선 (`fortune/services.py`)
  - GMS OpenAI 설정 (`config/settings.py`)
  - 아이템 분석 로직 수정 (`items/api_views.py`, `items/item_analyzer.py`)
  - 메뉴 요약 GMS GPT-5-nano 변경 (`recommendations/api_views.py`)
  - gunicorn 타임아웃 120s 증가 (`Procfile`)
- Frontend
  - 메뉴 UI 수정 (`Menu.vue`)
  - 아이템 세부 점수 로직 개편 (`similarity.js`)
  - 아이템 세부 페이지 UI 개선 (`ItemCheck.vue`, `Detail.vue`)
  - 운세 미생성 시 점수/색깔 출력 문제 해결 (`List.vue`)
  - axios 타임아웃 120s 증가 (`api.js`)

### 이수진
- Frontend
  - 모바일 환경 디자인 수정, 별자리/띠 배열, 로또번호 글씨 크기 (`Today.vue`)
  - 모바일 환경 메인화면 글씨 변경 (`Home.vue`)
  - 모바일 환경 스타일 (`style.css`)

---

## v1.3.0 (25.12.08)

### 장하선
- 배포
  - Vercel rewrites 설정 (`frontend/.env.production`, `frontend/vercel.json`)
  - PostgreSQL 연동 (`psycopg2-binary` 추가)
  - AWS EB 설정 파일 추가 (`.ebextensions/`, `Procfile`)
  - `settings.py` BASE_DIR 위치 수정

### 이수진
- Frontend
  - 네브바 버튼 링크 수정 (`Navbar.vue`)

---

## v1.2.0 (25.12.05)

### 장하선
- `frontend/src/views/items/Detail.vue` - 행운아이템 점수 계산로직 추가
- `frontend/src/views/items/List.vue` - 아이템 목록 카드 UI 개선
- `frontend/src/utils/colors.js` - 행운색 점수 계산로직 개선
- `ootd.json` - 후리스 중복 제거

### 이수진
- `frontend/src/assets/css/style.css` - 디자인 수정

### 김유림
- `frontend/src/assets/images/ootd/` - ootd 이미지 대량 추가/수정 (50개 이상)

---

## v1.1.0 (25.12.03)

### 장하선
- `frontend/src/views/fortune/ItemCheck.vue` - 행운지수 원형 및 색상 비교 정렬 개선
- `frontend/src/views/items/List.vue` - 아이템 목록 카드 UI 다크테마 적용, AI 분석 태그 표시
- `frontend/src/utils/colors.js` - color mapping 통합 js 파일로 전환
- `frontend/src/views/fortune/Today.vue` - 운세 텍스트 ul 형태로 수정

### 이수진
- `frontend/src/views/recommendations/Menu.vue` - 메뉴 UI 수정

---

## v1.0.6 (25.12.02)

### 장하선
- `frontend/src/views/recommendations/OOTD.vue` - 날씨 UI 수정, 시간별 예보 온도 그래프 추가
- `recommendations/api_views.py` - 날씨 API 연동

### 이수진
- `frontend/src/views/recommendations/Menu.vue` - 메뉴 추천 페이지 UI

### 김유림
- `frontend/src/views/fortune/Today.vue` - UI 전체 수정
- `frontend/src/views/items/Detail.vue`, `List.vue` - UI 수정
- `frontend/src/assets/zodiac/` - 별자리 아이콘 추가

---

## v1.0.5 (25.12.01)

### 장하선
- `frontend/src/views/fortune/ItemCheck.vue` - 아이템 이상현상 수정
- `frontend/src/views/auth/DeleteAccount.vue` - 회원 탈퇴 기능 추가
- `users/api_views.py` - 회원 탈퇴 시 정보 삭제

### 이수진
- `frontend/src/views/auth/Register.vue` - 비밀번호 요구사항 UI 변경
- `frontend/src/views/auth/Login.vue` - 비밀번호 요구사항 UI 변경

### 김유림
- `frontend/src/views/fortune/Today.vue` - 오늘의 운세 UI 수정
- `frontend/src/views/recommendations/Menu.vue` - 메뉴 UI 수정
- `frontend/src/components/Navbar.vue` - 네비바 문구 수정, '내 아이템' 메뉴 추가

---

## v1.0.4 (25.11.30)

### 장하선
- `config/settings.py` - S3 storage 설정
- `items/admin.py` - 아이템 관리자 페이지

### 이수진
- `frontend/src/views/items/List.vue` - AI 분석 태그 표시

---

## v1.0.3 (25.11.28)

### 장하선
- `items/api_views.py` - 아이템 업로드 S3 환경 수정
- `items/item_analyzer.py` - 아이템 색상 분석 로직
- `items/models.py` - 아이템 모델

### 이수진
- `frontend/src/views/fortune/ItemCheck.vue` - 아이템 체크 페이지

---

## v1.0.2 (25.11.27)

### 장하선
- `fortune/services.py` - 운세 계산 서비스
- `fortune/api_views.py` - 운세 API

### 이수진
- `frontend/src/views/fortune/Calculate.vue` - 운세 계산 페이지

---

## v1.0.1 (25.11.26)

### 장하선
- `config/` - Django 프로젝트 초기 설정
- `users/` - 사용자 모델 및 인증

### 이수진
- `frontend/` - Vue 프로젝트 초기 설정

---

## v1.0.0 (25.11.25)

- 프로젝트 킥오프
- 팀 역할 분배
- 개발 환경 설정