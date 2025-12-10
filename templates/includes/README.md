# Base Card Template System

Fortune Life 프로젝트의 재사용 가능한 카드 템플릿 시스템입니다.
웹과 모바일에서 일관된 디자인을 유지하며 반응형으로 동작합니다.

## 기본 구조

```html
{% extends 'base.html' %}

{% block content %}
<div class="page-container">
    <div class="content-wrapper">
        {# 페이지 헤더 #}
        {% include 'includes/page_header.html' with title="페이지 제목" subtitle="부제목" icon="fas fa-star" %}

        {# 카드 콘텐츠 #}
        <div class="card-base card-lg section-spacing">
            <h4 class="card-title text-center mb-4">
                <i class="fas fa-icon text-primary"></i>
                카드 제목
            </h4>
            <div class="card-body-section">
                {# 콘텐츠 #}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## 사용 가능한 클래스

### 컨테이너 클래스

| 클래스 | 설명 |
|--------|------|
| `.page-container` | 페이지 전체 래퍼 (패딩 자동 적용) |
| `.content-wrapper` | 콘텐츠 최대 너비 제한 (900px) |
| `.content-wrapper.wide` | 넓은 콘텐츠 영역 (1100px) |
| `.content-wrapper.narrow` | 좁은 콘텐츠 영역 (700px) |

### 카드 클래스

| 클래스 | 설명 |
|--------|------|
| `.card-base` | 기본 카드 스타일 (글래스모피즘) |
| `.card-lg` | 큰 패딩 (2.5rem) |
| `.card-md` | 중간 패딩 (1.5rem) |
| `.card-sm` | 작은 패딩 (1rem) |
| `.card-interactive` | 호버 시 상승 효과 |

### 카드 내부 구조

| 클래스 | 설명 |
|--------|------|
| `.card-header-section` | 카드 헤더 (하단 테두리) |
| `.card-header-section.no-border` | 테두리 없는 헤더 |
| `.card-body-section` | 카드 본문 |
| `.card-footer-section` | 카드 푸터 (상단 테두리) |
| `.card-footer-section.no-border` | 테두리 없는 푸터 |
| `.card-title` | 카드 제목 스타일 |

### 레이아웃 클래스

| 클래스 | 설명 |
|--------|------|
| `.card-grid` | CSS Grid 레이아웃 |
| `.card-grid.cols-2` | 2열 그리드 |
| `.card-grid.cols-3` | 3열 그리드 |
| `.card-grid.cols-4` | 4열 그리드 |
| `.card-row` | Flexbox 가로 배치 |
| `.section-spacing` | 섹션 간격 (2rem) |
| `.section-spacing-lg` | 큰 섹션 간격 (3rem) |

### 정보 박스

| 클래스 | 설명 |
|--------|------|
| `.info-box` | 기본 정보 박스 |
| `.info-box.info-primary` | 보라색 테마 |
| `.info-box.info-success` | 초록색 테마 |
| `.info-box.info-warning` | 노란색 테마 |
| `.info-box.info-danger` | 빨간색 테마 |
| `.info-box.info-info` | 파란색 테마 |

### 유틸리티 클래스

| 클래스 | 설명 |
|--------|------|
| `.badge-row` | 뱃지 가로 정렬 |
| `.action-buttons` | 버튼 그룹 (중앙 정렬) |
| `.action-buttons.left` | 좌측 정렬 |
| `.action-buttons.right` | 우측 정렬 |
| `.text-content` | 텍스트 콘텐츠 스타일 |
| `.text-content.text-lg` | 큰 텍스트 |
| `.empty-state` | 빈 상태 표시 |

## 재사용 가능한 컴포넌트

### 1. 페이지 헤더 (page_header.html)

```django
{% include 'includes/page_header.html' with title="오늘의 운세" subtitle="당신의 오늘을 빛낼 운세를 확인해보세요" icon="fas fa-crystal-ball" %}
```

변수:
- `title`: 페이지 타이틀 (필수)
- `subtitle`: 부제목 (선택)
- `icon`: Font Awesome 아이콘 클래스 (선택)
- `icon_color`: 아이콘 색상 클래스 (선택, 기본: text-primary)

### 2. 빈 상태 (empty_state.html)

```django
{% include 'includes/empty_state.html' with icon="fas fa-inbox" title="데이터 없음" text="아직 데이터가 없습니다" button_text="추가하기" button_url="/add" button_icon="fas fa-plus" %}
```

변수:
- `icon`: Font Awesome 아이콘 클래스 (선택)
- `title`: 제목 (필수)
- `text`: 설명 텍스트 (선택)
- `button_text`: 버튼 텍스트 (선택)
- `button_url`: 버튼 URL (선택)
- `button_icon`: 버튼 아이콘 (선택)

### 3. 정보 박스 (info_box.html)

```django
{% include 'includes/info_box.html' with type="primary" content="정보 내용" icon="fas fa-info-circle" %}
```

변수:
- `type`: 박스 타입 (primary/success/warning/danger/info)
- `content`: 내용 텍스트 (필수)
- `icon`: Font Awesome 아이콘 클래스 (선택)
- `class`: 추가 CSS 클래스 (선택)

## 반응형 동작

- **데스크톱 (992px+)**: 기본 레이아웃
- **태블릿 (768px-992px)**: 4열 → 2열, 3열 → 2열
- **모바일 (768px-)**: 모든 그리드 1열, 카드 row 세로 배치
- **작은 모바일 (480px-)**: 더 작은 패딩, 작은 타이틀

## 예시: 새 페이지 만들기

```django
{% extends 'base.html' %}

{% block title %}새 페이지 - Fortune Life{% endblock %}

{% block content %}
<div class="page-container">
    <div class="content-wrapper">
        {% include 'includes/page_header.html' with title="새 페이지" subtitle="페이지 설명" icon="fas fa-star" %}

        {# 메인 카드 #}
        <div class="card-base card-lg section-spacing">
            <h4 class="card-title text-center mb-4">
                <i class="fas fa-info-circle text-primary"></i>
                메인 콘텐츠
            </h4>
            <div class="text-content">
                여기에 콘텐츠를 작성하세요.
            </div>
        </div>

        {# 2열 그리드 카드 #}
        <div class="card-grid cols-2 section-spacing">
            <div class="card-base card-md card-interactive text-center">
                <i class="fas fa-heart fa-3x text-danger mb-3"></i>
                <h5 class="text-white">카드 1</h5>
                <p class="text-white opacity-75 small mb-4">설명</p>
                <a href="#" class="btn btn-outline-light rounded-pill px-4">
                    버튼 <i class="fas fa-arrow-right ms-2"></i>
                </a>
            </div>
            <div class="card-base card-md card-interactive text-center">
                <i class="fas fa-star fa-3x text-warning mb-3"></i>
                <h5 class="text-white">카드 2</h5>
                <p class="text-white opacity-75 small mb-4">설명</p>
                <a href="#" class="btn btn-outline-light rounded-pill px-4">
                    버튼 <i class="fas fa-arrow-right ms-2"></i>
                </a>
            </div>
        </div>

        {# 정보 박스 #}
        <div class="card-base card-lg">
            <h4 class="card-title text-center mb-4">
                <i class="fas fa-lightbulb text-warning"></i>
                정보 박스 예시
            </h4>
            <div class="card-row">
                <div class="info-box info-primary text-center">
                    <span class="d-block mb-2">Primary</span>
                    <p class="text-white opacity-75 small mb-0">보라색 테마</p>
                </div>
                <div class="info-box info-success text-center">
                    <span class="d-block mb-2">Success</span>
                    <p class="text-white opacity-75 small mb-0">초록색 테마</p>
                </div>
                <div class="info-box info-warning text-center">
                    <span class="d-block mb-2">Warning</span>
                    <p class="text-white opacity-75 small mb-0">노란색 테마</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```
