# 📋 업데이트 내역

## v1.8.6 (25.12.23)

### 장하선
- Frontend
  - 홈 화면 '운세 보기' 버튼 클릭 안 되는 문제 수정 (`Home.vue`)
  - 사용되지 않는 빈 파일 삭제 (`assets/main.css`)
  - CSS 중복 코드 정리 (`assets/css/style.css`)
    - 중복된 `.animate-float`, `@keyframes float` 정의 제거
    - 중복된 `.hover-lift` 정의 통합 (box-shadow 포함 버전 유지)
- Backend
  - 미사용 파일 삭제 (`items/word_similarity.py`, 372줄)
  - 캐시 함수 중복 제거 및 리팩토링 (`fortune/api_views.py`)
    - 770줄 → 562줄로 208줄 감소
    - 중복 캐시 함수 제거, `FortuneCacheManager` 클래스 사용으로 통합
    - 일간/주간/월간 캐시 로직 `cache_manager.py`로 일원화

### 김유림
- Frontend
  - 마이페이지 아이템 카테고리 필터링 기능 추가 (`MyPage.vue`)
    - 전체/의류/액세서리/기타 카테고리 버튼 추가
    - 선택한 카테고리별 아이템 필터링
    - 소분류(sub_category) 태그 표시
  - 아이템 카테고리 옵션 정리 (`Upload.vue`, `Detail.vue`)
    - 화장품, 전자제품 옵션 제거 (의류, 액세서리, 기타만 유지)
  - `/items` 페이지 제거 및 라우팅 변경 (`router/index.js`, `List.vue` 삭제)
    - 아이템 업로드/등록/삭제 후 `/mypage`로 이동하도록 변경
  - 마이페이지 행운색/카테고리 블록 순서 변경 (`MyPage.vue`)
    - 오늘의 행운색을 위로, 카테고리 버튼을 아래로 배치
  - 행운색 표시 레이아웃 개선 (`MyPage.vue`)
    - 항상 세로 2줄 배치 (라벨 위, 색상들 아래)
  - 홈화면 밤하늘 애니메이션 추가 (`Home.vue`)
  - 사이트 소개 페이지 추가 및 홈 스크롤 애니메이션 개선 (`About.vue`, `Home.vue`)
  - 모바일 환경 애니메이션 효과 추가 및 스크롤 성능 최적화
  - iOS Safari 스크롤 성능 개선 - RAF 폴링 대신 passive 이벤트 사용
  - 로그인 아이디 입력 시 한글 경고 메시지 추가 (`Login.vue`)
  - 이메일 로고 관련 수정 (캐시 무효화, 첨부파일 제거, 로고 변경)
- Backend
  - 이메일 로고 'Lucky Picky'로 변경

### 이수진
- Frontend
  - 메인 화면 문구 색상과 버튼 색상 수정 (`Home.vue`)
  - 메인 화면 아이템 행운도 이름과 이미지 변경 (이름: 아이템 행운도 분석, 이미지: 돋보기)
  - 아이템 행운도 "측정" → "분석"으로 멘트 변경
  - 메뉴 추천 → 오늘의 메뉴 추천 멘트 변경 (`Menu.vue`)
  - 오늘의 메뉴 추천 창에서 오늘의 행운색 배열 변경 (OOTD 추천창과 동일하게)
  - 사이트 소개 주요 기능 멘트 일부 수정 (OOTD 아이콘 메인과 동일하게) (`About.vue`)
  - 회원 탈퇴 확인창 버튼 색상 수정 (`DeleteAccount.vue`)
  - 아이폰 Safari 스크롤 지연 문제 해결 시도
  - 모바일 환경 추천 액세서리 배열 변경 및 이미지 중앙 정렬 (`OOTD.vue`)
  - OOTD 아이콘 변경 (화살표 유무, 색상 변경)
  - 이메일 로고 변경

---

## v1.8.4 (25.12.22)

### 장하선
- Frontend
  - 메인 화면 카드 영역 전체 클릭 가능하도록 수정 (`Home.vue`)
  - 내부 카드 정렬 기준 아래쪽 기준으로 변경
  - OOTD 고정 크기 카드 추가 및 옷 이미지 영역 고정 박스 적용 (`OOTD.vue`)
  - 메뉴 추천 페이지 행운색에 팔레트 아이콘 추가 (`Menu.vue`)
  - OOTD 아이콘 전체 3D 아이콘으로 수정
  - favicon 이모지 변경
  - 스카프 → 머플러 용어 수정

### 김유림
- Frontend
  - 마이페이지 프로필 설정 블록 스타일 적용 (`MyPage.vue`)
  - 추천 카드 블록 전체 클릭 가능하도록 수정 (`Fortune.vue`)
  - 아이템 분석 중 오버레이 추가 (`ItemCheck.vue`)
  - 베이지/아이보리/크림 색상 HEX 코드 수정 (`colors.js`)
  - colorMap에 베이지 색상 변형 추가
  - 아이템 분석 로직 수정: 아이템 이름 대신 분석 태그 결과로 분석하도록 변경
  - 홈 화면 문구 수정: "식사" → "메뉴", "AI 기반 운세 & 라이프스타일" 제거
  - 모바일 반응형 UI 개선
    - 버튼/태그들이 한 줄로 표시되도록 `flex-nowrap` 적용 (`ItemCheck.vue`, `Upload.vue`)
    - OOTD 추천 액세서리 설명 텍스트 제거
    - OOTD 페이지 행운색 가로 배치로 변경
    - OOTD 페이지 액세서리 이미지 가운데 정렬
    - 프로필 페이지 제목 가운데 정렬 및 섹션 구분선 추가

### 이수진
- Frontend
  - 마이페이지 신규 생성 (`MyPage.vue`)
    - 프로필 아이콘 색상 수정
    - 프로필 글씨 크기 수정
    - 기본정보/추가정보 글자 중앙 정렬
    - 추가정보 위 구분선 추가
  - 모바일 환경 UI 개선
    - 메인화면 글씨 줄바꿈 정상화
    - 아이템 업로드창 버튼 크기 수정
    - 운세확인 창 추천받기 버튼 마진 여백 수정
    - OOTD 추천창 행운색 표기 정렬 변경
    - 추천 액세서리 이미지 중앙 정렬
    - 아이템 분석 창에 오늘의 행운템 블록 추가
  - 제목 옆 아이콘 전면 수정
  - OOTD 추천 아이콘 크기 확대
- Assets
  - 행운템 이미지 변경 (귀걸이, 반지, 책갈피, 카드지갑, 괄사, 손수건, 립밤, 스카프)
  - 음식 이미지 변경 (된장찌개, 곱창, 해장국, 불고기, 갈비찜, 갈비탕)
- Data
  - 팥빙수 색상 빨간색 → 흰색으로 수정

---

## v1.8.3 (25.12.21)

### 장하선
- Backend
  - S3 이미지 URL 문제 해결 (`items/models.py`, `items/api_views.py`, `fortune/api_views.py`)
    - 문제: S3에 이미지 업로드는 되지만 프론트엔드에서 이미지가 표시되지 않음
    - 원인: CloudFront가 `/items/*` 경로를 S3가 아닌 EB로 라우팅하여 404 반환
    - 해결: `image_full_url` property 추가 - S3 절대 URL 직접 생성
    - `item.image.url` → `item.image_full_url`로 변경 (API 응답에서 S3 직접 URL 반환)
  - 백엔드 코드 리팩토링 (`fortune/services.py` 삭제)
    - 1107줄짜리 거대한 단일 파일 `services.py` 제거
    - 리팩토링된 `fortune/services/` 패키지 사용으로 전환
    - `FortuneCalculator` 클래스 중복 제거
  - 설정 개선 (`config/settings.py`)
    - `ALERT_FROM_EMAIL`, `ALERT_RECIPIENT_LIST` 환경변수 추가
    - 하드코딩된 이메일 주소 환경변수화
- Frontend
  - 사용되지 않는 코드 정리
    - `frontend/src/api/fortune.js` 삭제 (미사용 파일)
    - `frontend/src/api/` 폴더 삭제
  - 아이템 업로드 UI 정리 (`Upload.vue`)
    - 사용하지 않는 즐겨찾기 체크박스 제거

---

## v1.8.2 (25.12.21)

### 김유림
- Backend
  - 배포 환경 ALLOWED_HOSTS 설정 수정 (`config/settings.py`)
    - 문제: Vercel 프론트엔드에서 백엔드 API 호출 시 500 에러 발생
    - 원인: Django가 특정 IP 주소를 허용된 호스트로 인식하지 못함
    - 해결:
      - DEBUG 모드에서 모든 호스트 허용 (`ALLOWED_HOSTS = ['*']`)
      - AWS EC2 서버의 공인/사설 IP 자동 추가
      - CloudFront 프록시 요청 처리 설정 추가
    - 결과: 프론트엔드에서 백엔드 API 정상 호출 가능
- Deployment
  - AWS Elastic Beanstalk 배포 완료 (2025-12-21 19:35)

---

## v1.8.1 (25.12.20)

### 김유림
- Backend
  - 메뉴 추천 API 버그 수정 및 로직 개선 (`recommendations/api_views.py`)
    - ZeroDivisionError 수정: 빈 행운색 배열 처리
    - 행운색 3개 모두 순환하여 추천 메뉴에 적용
    - 그라데이션 배경 로직 단순화
    - 행운색 매칭 로직 개선
    - 디버깅 로그 추가 (추천 생성/로드 시 개수 출력)
- Frontend
  - 운세 페이지 탭 내용 표시 안 되는 버그 수정 (`Fortune.vue`)
    - 문제: 종합운 외 다른 탭(애정운, 금전운, 직장운 등) 클릭 시 내용이 표시되지 않음
    - 원인: Bootstrap 탭 방식과 Vue 충돌
    - 해결: Vue 방식(`v-show`, `@click.prevent`)으로 탭 전환 로직 재구현
  - 운세 페이지 UI 개선 (`Fortune.vue`)
    - 기간 선택 버튼 가운데 정렬
    - 탭 점수 바에 애니메이션 효과 추가
    - 연애운 → 애정운 용어 변경
    - 직장운 CSS 클래스 오타 수정
  - 네비게이션바 로고 변경 (`Navbar.vue`)
    - 로고 이미지 경로 업데이트

---

## v1.8.0 (25.12.18)

### 장하선
- Backend
  - GMS Embedding API 기반 아이템 유사도 엔드포인트 추가 (`items/api_views.py`, `items/api_urls.py`)
    - `POST /api/items/similarity/`: text-embedding-3-small 모델로 코사인 유사도 계산
    - 아이템 이름과 행운 아이템 간 의미적 유사도 반환
  - `requirements.txt`에 numpy 의존성 추가
- Frontend
  - 하이브리드 아이템 유사도 계산 로직 구현 (`itemSimilarity.js`, `luckScore.js`)
    - `getHybridSimilarity()`: FastText(즉시) + GMS Embedding(비동기) 중 높은 값 반환
    - `calculateLuckScoreAsync()`: 비동기 하이브리드 점수 계산 함수 추가
  - 아이템 상세 페이지 하이브리드 점수 적용 (`Detail.vue`)
    - 페이지 로드 시 FastText 점수 즉시 표시 → GMS 결과가 높으면 자동 업데이트
  - 행운 점수 공식 조정 (`luckScore.js`)
    - 기본 20점 → 35점, 색상 40점 → 35점, 아이템 40점 → 30점
  - 아이템 상세 페이지 라우트 변경 감지 버그 수정 (`Detail.vue`)
    - `watch(route.params.id)` 추가: 같은 컴포넌트 내 다른 아이템 이동 시 데이터 갱신

### 김유림
- Backend
  - 메뉴 추천 로직 개선
    - 3가지 행운색 모두 고려하여 추천 점수 산출
    - 추천 메뉴 항상 2개 표시 보장 (행운색 음식 부족 시 전체 음식 중 랜덤 선택)
    - 메뉴 추천 목록에서 음식의 실제 색상 정보 표시 기능 추가
  - OOTD 추천 개선
    - 퍼스널 컬러 필터링 로직 적용
  - 이메일 서비스 개선 (Email Service)
    - 서비스 명칭 브랜딩: 'Lucky Picky' 적용
    - 이메일 제목 및 템플릿 디자인 변경 (다크 테마 적용)
    - HTML 이메일 템플릿 적용 및 로고 이미지 삽입
- Frontend
  - Assets
    - 로고 이미지를 외부 링크에서 프로젝트 정적 리소스(`assets`)로 변경하여 안정성 확보
      
---

## v1.8.0 (25.12.18)

### 장하선
- Backend
  - 스파게티 코드 리팩토링 (`fortune/constants/`, `fortune/services.py`)
    - 색상, 아이템, 템플릿 상수를 별도 모듈로 분리 (colors.py, items.py, templates.py)
    - 중복 코드 제거 및 유틸리티 함수 통합
  - 점수별 톤 가이드 추가 (`fortune/services.py`)
    - `_get_tone_for_score()`: 점수 구간별 톤 설명 반환 (매우 긍정적/긍정적/보통/다소 부정적/부정적)
    - `_build_score_tone_guide()`: LLM 프롬프트용 점수 정보 및 톤 가이드 생성
    - 운세 텍스트가 점수와 일관되게 생성되도록 개선 (55점에 긍정적 멘트 방지)
  - MBTI별 톤 가이드 추가 (`fortune/services.py`)
    - `_get_mbti_tone_guide()`: 16가지 MBTI 유형별 맞춤 스타일 가이드
    - 분석가형(NT), 외교관형(NF), 관리자형(SJ), 탐험가형(SP) 그룹별 특성 반영
    - LLM 프롬프트에 MBTI 맞춤 스타일 안내 추가
  - 퍼스널컬러 기반 행운색 로직 추가 (`fortune/constants/colors.py`, `fortune/services.py`)
    - `PERSONAL_COLOR_PALETTES`: 봄웜/여름쿨/가을웜/겨울쿨 유형별 어울리는 색상 풀
    - `PERSONAL_COLOR_AVOID`: 유형별 피해야 할 색상 목록
    - `_determine_lucky_colors()`: 퍼스널컬러 우선순위 적용 및 부적합 색상 필터링
  - `calculate_fortune()` 함수에 `personal_color` 파라미터 추가 (`fortune/services.py`)
  - API Views personal_color 전달 추가 (`fortune/api_views.py`, `recommendations/api_views.py`)
    - 일간/주간/월간 운세 생성 시 퍼스널컬러 정보 전달
    - 아이템 체크, 추천 API에도 퍼스널컬러 적용
  - 캐시 키 버전 v10 → v11 변경 (MBTI/퍼스널컬러 반영)
- Frontend
  - 주간/월간 운세에서 일간 전용 섹션 숨김 처리 (`Fortune.vue`)
    - 행운색, 행운아이템, 로또번호 섹션을 일간 운세에서만 표시
    - `selectedPeriod === 'daily'` 조건 추가
  - 행운 아이템 클릭 시 스크롤 버그 수정 (`Fortune.vue`)
    - `@click.stop.prevent` 이벤트 수식어 추가

---

## v1.7.3 (25.12.17)

### 장하선
- Backend
  - 비로그인 사용자 주간/월간 운세 중복 생성 문제 디버깅 (`fortune/api_views.py`)
    - `find_same_condition_weekly_fortune`, `find_same_condition_monthly_fortune` 함수에 상세 디버그 로그 추가
    - 3차 검색 로직: 정확히 일치 → gender 빈값 fallback → 기존 캐시 조건 불일치 확인
  - 주간/월간 운세 식별 키 생성 로직 추가 (`fortune/api_views.py`)
    - POST 요청 시 birth_date, gender 기반 캐시 저장/조회 로직 개선
- Frontend
  - 비로그인 사용자 운세 체크 로직 Store 기반으로 변경 (`Fortune.vue`)
    - 일간/주간/월간 운세 Store 캐시 확인 후 API 호출 생략
  - 비로그인 사용자 주간/월간 운세 확인 시 로딩 페이지 리다이렉트 버그 수정 (`Fortune.vue`, `Loading.vue`)
- Data
  - FastText 아이템 유사도 매트릭스 스케일링 (`data/itemSimilarity.json`)
    - 원본 범위 (0.3~0.6826) → 새 범위 (0.4~0.9)로 Min-Max 스케일링
    - 유사도 차이를 더 명확하게 반영하도록 개선

### 김유림
- Frontend
  - 로그인/회원가입 아이디 영문, 숫자만 입력 가능하도록 제한 (`Login.vue`, `Register.vue`)
  - 비로그인 사용자 운세 체크 로직을 Store 기반으로 변경 (`router/index.js`)

### 이수진
- Frontend
  - 프론트엔드에서 색상 HEX 값을 colorMap으로 재매핑 (`ItemCheck.vue`)
  - 아이보리/크림/베이지 색상을 흰색(#f3f4f6)으로 통일 (`colors.js`)
- Backend
  - 아이템 분석 색상 매핑 통일 (`item_analyzer.py`)

---

## v1.7.2 (25.12.17)

### 장하선
- Backend
  - 운세 점수 85점 고정 문제 해결 (`fortune/services.py`)
    - LLM 프롬프트에서 점수 정보 완전 제거 (텍스트만 생성하도록 변경)
    - 캐시 키 버전 v6 → v7 변경
    - 해결 방법: Django Admin에서 DailyFortuneCache, WeeklyFortuneCache, MonthlyFortuneCache 모두 삭제 필요
    - 점수는 백엔드 `_calculate_all_fortunes`에서 사주/오행 기반으로 계산 (50~100점 범위)

---

## v1.7.1 (25.12.17)

### 장하선
- Backend
  - Django Admin 타임스탬프 초 단위 표시 수정 (`fortune/admin.py`)
    - `format_datetime_kst` 함수 추가, KST 변환 및 `format_html` 사용
    - DailyFortuneCache, WeeklyFortuneCache, MonthlyFortuneCache Admin에 `created_at_display` 메서드 적용
  - 운세 점수 LLM 복사 문제 수정 시도 (`fortune/services.py`)
    - LLM 프롬프트 JSON 응답 예시에서 `scores` 필드 제거 (주간/월간/일간 모두)
    - 백엔드에서 LLM 응답의 `scores` 무시하도록 수정 (자체 계산 점수 사용)
    - 캐시 키 버전 v5 → v6 변경
- Frontend
  - 비로그인 사용자 운세 로딩 페이지 리다이렉트 수정 (`Loading.vue`)
    - 주간/월간 운세 생성을 `setTimeout`으로 분리하여 리다이렉트 차단 방지
  - 비로그인 사용자 Fortune Store 캐시 사용 로직 추가 (`Fortune.vue`)
    - 일일 운세 Store 데이터 있으면 API 호출 생략하도록 early return 추가
  - 아이템 업로드 UI 개선 (`Upload.vue`)
    - 카메라/갤러리 선택 버튼 추가
    - 이미지 미리보기 클릭 시 재선택 가능
  - 아이템 추천 로직 개선 (`ItemCheck.vue`)
    - 행운 점수 70점 미만일 때 다른 아이템 추천 (80점 이상만)
    - 추천할 좋은 아이템 없을 때 아이템 등록 유도 UI 추가

---

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
  - FastText 기반 아이템 유사도 시스템 구현 (꼬맨틀/Semantle-ko 방식)
    - 행운 점수 계산 로직 변경: 색상 40% + 아이템 유사도 60% (`ItemCheck.vue`, `Detail.vue`)
    - FastText (cc.ko.300) 코사인 유사도 기반 아이템 매칭 유틸리티 (`utils/itemSimilarity.js`)
  - 행운 지수 바로 표시, UI 수정 (`Detail.vue`)
  - "오늘의 운세" → "운세 확인하기" (`Navbar.vue`)
  - Fortune.vue 라우팅 변경 (`router/index.js`)
  - 주간/월간 운세 스토어 추가 (`fortune.js`)
- Data
  - food.json id 1칸씩 당김
  - FastText 사전 계산 유사도 매트릭스 추가 (88개 키워드, 1168개 유사도 쌍) (`data/itemSimilarity.json`)
- Scripts
  - FastText 유사도 매트릭스 생성 스크립트 (`scripts/generate_similarity_matrix.py`)
- etc
  - README.md 업데이트 및 UPDATE.md 추가

### 이수진
- Frontend
  - 마파두부, 해물파전, 잔치국수, 어묵탕, 감자탕, 곰탕 이미지 변경 (`assets/images/food/`)
  - menu.vue 데이터와 다른 이미지 삭제 (`Menu.vue`)

### 김유림
- Backend
  - 별자리별 아이템 3~4개로 확장, 날짜별 순환 표시 (`fortune/services.py`)
  - 유사 아이템 통합 (머플러→스카프, 펜던트→목걸이 등)
- Frontend
  - 행운 아이템 이모지를 PNG 이미지로 교체 (`Fortune.vue`)
  - 행운 아이템 이미지 30개 추가 (`assets/images/lucky_items/`)
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
- Frontend
  - 행운아이템 점수 계산로직 추가 (`Detail.vue`)
  - 아이템 목록 카드 UI 개선 (`List.vue`)
  - 행운색 점수 계산로직 개선 (`colors.js`)
- Data
  - 후리스 중복 제거 (`ootd.json`)

### 이수진
- Frontend
  - 디자인 수정 (`style.css`)

### 김유림
- Frontend
  - ootd 이미지 대량 추가/수정 - 50개 이상 (`assets/images/ootd/`)

---

## v1.1.0 (25.12.03)

### 장하선
- Frontend
  - 행운지수 원형 및 색상 비교 정렬 개선 (`ItemCheck.vue`)
  - 아이템 목록 카드 UI 다크테마 적용, AI 분석 태그 표시 (`List.vue`)
  - color mapping 통합 js 파일로 전환 (`colors.js`)
  - 운세 텍스트 ul 형태로 수정 (`Today.vue`)

### 이수진
- Frontend
  - 메뉴 UI 수정 (`Menu.vue`)

---

## v1.0.6 (25.12.02)

### 장하선
- Backend
  - 날씨 API 연동 (`recommendations/api_views.py`)
- Frontend
  - 날씨 UI 수정, 시간별 예보 온도 그래프 추가 (`OOTD.vue`)

### 이수진
- Frontend
  - 메뉴 추천 페이지 UI (`Menu.vue`)

### 김유림
- Frontend
  - UI 전체 수정 (`Today.vue`)
  - UI 수정 (`Detail.vue`, `List.vue`)
  - 별자리 아이콘 추가 (`assets/zodiac/`)

---

## v1.0.5 (25.12.01)

### 장하선
- Backend
  - 회원 탈퇴 시 정보 삭제 (`users/api_views.py`)
- Frontend
  - 아이템 이상현상 수정 (`ItemCheck.vue`)
  - 회원 탈퇴 기능 추가 (`DeleteAccount.vue`)

### 이수진
- Frontend
  - 비밀번호 요구사항 UI 변경 (`Register.vue`, `Login.vue`)

### 김유림
- Frontend
  - 오늘의 운세 UI 수정 (`Today.vue`)
  - 메뉴 UI 수정 (`Menu.vue`)
  - 네비바 문구 수정, '내 아이템' 메뉴 추가 (`Navbar.vue`)

---

## v1.0.4 (25.11.30)

### 장하선
- Backend
  - S3 storage 설정 (`config/settings.py`)
  - 아이템 관리자 페이지 (`items/admin.py`)

### 이수진
- Frontend
  - AI 분석 태그 표시 (`List.vue`)

---

## v1.0.3 (25.11.28)

### 장하선
- Backend
  - 아이템 업로드 S3 환경 수정 (`items/api_views.py`)
  - 아이템 색상 분석 로직 (`items/item_analyzer.py`)
  - 아이템 모델 (`items/models.py`)

### 이수진
- Frontend
  - 아이템 체크 페이지 (`ItemCheck.vue`)

---

## v1.0.2 (25.11.27)

### 장하선
- Backend
  - 운세 계산 서비스 (`fortune/services.py`)
  - 운세 API (`fortune/api_views.py`)

### 이수진
- Frontend
  - 운세 계산 페이지 (`Calculate.vue`)

---

## v1.0.1 (25.11.26)

### 장하선
- Backend
  - Django 프로젝트 초기 설정 (`config/`)
  - 사용자 모델 및 인증 (`users/`)

### 이수진
- Frontend
  - Vue 프로젝트 초기 설정 (`frontend/`)

---

## v1.0.0 (25.11.25)

- 프로젝트 킥오프
- 팀 역할 분배
- 개발 환경 설정
