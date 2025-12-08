# AWS EB HTTPS 설정 가이드

Vercel(HTTPS)에서 AWS EB(HTTP)로 요청하면 Mixed Content 오류가 발생합니다.
CloudFront를 사용하여 HTTPS를 활성화하는 방법입니다.

## CloudFront 설정 단계

### 1. AWS Console에서 CloudFront 접속
https://console.aws.amazon.com/cloudfront

### 2. "Create Distribution" 클릭

### 3. Origin 설정
- **Origin Domain**: `pjt-env.eba-jnmm8j7x.ap-northeast-2.elasticbeanstalk.com`
- **Protocol**: HTTP only (EB는 HTTP만 지원하므로)
- **HTTP Port**: 80

### 4. Default Cache Behavior 설정
- **Viewer Protocol Policy**: Redirect HTTP to HTTPS
- **Allowed HTTP Methods**: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
- **Cache Policy**: CachingDisabled (API는 캐시하면 안됨)
- **Origin Request Policy**: AllViewer

### 5. Settings
- **Price Class**: Use only North America and Europe (비용 절감) 또는 All edge locations
- **Default Root Object**: 비워둠

### 6. Create Distribution 클릭

### 7. 배포 완료 대기 (약 5-10분)
Status가 "Deployed"로 변경될 때까지 대기

### 8. CloudFront 도메인 확인
예: `d1234567890.cloudfront.net`

### 9. Frontend 환경변수 업데이트
`.env.production` 파일에서:
```
VITE_API_BASE_URL=https://d1234567890.cloudfront.net
```

### 10. Vercel 재배포
```bash
cd frontend
npm run build
vercel --prod
```

## 주의사항

1. **CORS 설정**: Django settings.py에서 CloudFront 도메인을 CORS_ALLOWED_ORIGINS에 추가해야 합니다.

2. **캐시 무효화**: API 응답이 캐시되면 안되므로 Cache Policy를 "CachingDisabled"로 설정하세요.

3. **비용**: CloudFront는 데이터 전송량에 따라 요금이 발생하지만, 소규모 트래픽은 프리티어로 커버됩니다.

## 대안: Application Load Balancer (ALB)

EB 환경을 Single Instance에서 Load Balanced로 변경하면 ACM 인증서를 직접 연결할 수 있습니다.
하지만 이는 추가 비용이 발생합니다 (ALB 시간당 요금).

### ALB 설정 방법
1. EB Console → Configuration → Capacity
2. Environment type: Load balanced 선택
3. Load balancer type: Application Load Balancer
4. ACM에서 인증서 발급 (도메인 필요)
5. HTTPS 리스너 추가 (443 포트)
