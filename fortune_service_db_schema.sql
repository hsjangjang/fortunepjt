-- =====================================================
-- 운세 기반 일상 추천 서비스 DB Schema
-- =====================================================

-- 1. 사용자 관련 테이블
-- =====================================================
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    birth_time TIME,  -- 태어난 시각 (선택)
    gender ENUM('M', 'F', 'OTHER') NOT NULL,
    chinese_name VARCHAR(100),  -- 한자 이름 (선택)
    mbti VARCHAR(4),  -- MBTI 유형
    personal_color VARCHAR(50),  -- 퍼스널컬러 (봄웜톤, 여름쿨톤 등)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_birth_date (birth_date)
);

-- 2. 운세 캐싱 테이블 (하루 동안 고정된 운세 저장)
-- =====================================================
CREATE TABLE daily_fortune_cache (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    session_key VARCHAR(255),  -- 비회원용 세션 키
    fortune_date DATE NOT NULL,
    fortune_score INT,  -- 오늘의 운세 점수 (1-100)
    fortune_text TEXT,  -- 운세 내용
    lucky_color VARCHAR(7),  -- HEX 색상 코드
    lucky_colors JSON,  -- 복수 색상 저장 [{color: '#FF0000', weight: 0.8}]
    lucky_number INT,
    lucky_direction VARCHAR(20),
    zodiac_sign VARCHAR(20),  -- 별자리
    chinese_zodiac VARCHAR(20),  -- 띠
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, fortune_date),
    INDEX idx_session_date (session_key, fortune_date)
);

-- 3. 사용자 아이템 저장 테이블
-- =====================================================
CREATE TABLE user_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    item_name VARCHAR(200),
    item_category VARCHAR(50),  -- 상의, 하의, 악세서리, 가방 등
    image_url VARCHAR(500),
    dominant_colors JSON,  -- AI 분석 색상 [{color: '#FF0000', percentage: 45}]
    ai_analysis_result JSON,  -- AI 분석 상세 결과
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_items (user_id, item_category)
);

-- 4. 일일 추천 기록 테이블
-- =====================================================
CREATE TABLE daily_recommendations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    session_key VARCHAR(255),
    recommendation_date DATE NOT NULL,
    recommendation_type ENUM('OOTD', 'MENU', 'ITEM', 'ACTIVITY') NOT NULL,
    recommendation_data JSON,  -- 추천 상세 내용
    weather_data JSON,  -- 날씨 정보 (온도, 습도, 강수확률 등)
    user_feedback INT,  -- 1-5 평점
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_rec_date (recommendation_date, user_id)
);

-- 5. OOTD 추천 상세 테이블
-- =====================================================
CREATE TABLE ootd_recommendations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    recommendation_id BIGINT NOT NULL,
    top_color VARCHAR(7),  -- 상의 색상
    bottom_color VARCHAR(7),  -- 하의 색상
    outer_required BOOLEAN,
    outer_color VARCHAR(7),
    sleeve_type ENUM('SHORT', 'LONG', 'SLEEVELESS'),
    style_tags JSON,  -- ['캐주얼', '오피스룩', '데이트룩']
    matching_score FLOAT,  -- 행운 색상과의 매칭 점수
    FOREIGN KEY (recommendation_id) REFERENCES daily_recommendations(id) ON DELETE CASCADE
);

-- 6. 메뉴 추천 상세 테이블
-- =====================================================
CREATE TABLE menu_recommendations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    recommendation_id BIGINT NOT NULL,
    menu_name VARCHAR(200),
    menu_category VARCHAR(50),  -- 한식, 중식, 일식, 양식 등
    menu_color_match JSON,  -- 색상 매칭 정보
    calories INT,
    recipe_link VARCHAR(500),
    restaurant_suggestion VARCHAR(200),
    FOREIGN KEY (recommendation_id) REFERENCES daily_recommendations(id) ON DELETE CASCADE
);

-- 7. 색상 마스터 데이터 테이블
-- =====================================================
CREATE TABLE color_master (
    id INT PRIMARY KEY AUTO_INCREMENT,
    color_code VARCHAR(7) NOT NULL,
    color_name VARCHAR(50),
    color_category VARCHAR(30),  -- 웜톤, 쿨톤 등
    rgb_r INT,
    rgb_g INT,
    rgb_b INT,
    hsl_h INT,
    hsl_s INT,
    hsl_l INT,
    meaning TEXT,  -- 색상의 의미
    fortune_keywords JSON,  -- 운세 관련 키워드
    UNIQUE KEY unique_color (color_code)
);

-- 8. 사주/운세 기본 데이터 테이블
-- =====================================================
CREATE TABLE fortune_base_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category VARCHAR(50),  -- 천간, 지지, 오행 등
    code VARCHAR(20),
    name_ko VARCHAR(50),
    name_cn VARCHAR(50),
    attributes JSON,  -- 속성 정보
    compatibility JSON  -- 상성/상극 정보
);

-- 9. MBTI별 말투 템플릿 테이블
-- =====================================================
CREATE TABLE mbti_speech_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    mbti_type VARCHAR(4),
    category VARCHAR(50),  -- 인사말, 추천, 위로, 격려 등
    template_text TEXT,
    tone VARCHAR(20)  -- formal, casual, friendly 등
);

-- 10. 사용자 선호도 학습 테이블
-- =====================================================
CREATE TABLE user_preferences (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    preference_type VARCHAR(50),  -- color, style, food 등
    preference_value VARCHAR(200),
    score FLOAT,  -- 선호도 점수
    interaction_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_pref (user_id, preference_type)
);

-- 11. API 로그 테이블 (LLM 호출 등)
-- =====================================================
CREATE TABLE api_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    api_type VARCHAR(50),  -- openai, claude, image_analysis 등
    request_data JSON,
    response_data JSON,
    tokens_used INT,
    response_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_api_logs (user_id, api_type, created_at)
);
