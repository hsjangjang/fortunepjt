import requests
from django.conf import settings

def get_korean_address(lat, lon):
    """카카오 API로 좌표를 한글 행정동으로 변환"""
    kakao_api_key = settings.KAKAO_REST_API_KEY

    if not kakao_api_key or kakao_api_key == 'your-kakao-rest-api-key-here':
        return None

    try:
        # 카카오 로컬 API - 좌표 -> 주소 변환
        url = f"https://dapi.kakao.com/v2/local/geo/coord2address.json?x={lon}&y={lat}"
        headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
        response = requests.get(url, headers=headers, timeout=3)

        if response.status_code != 200:
            print(f"[DEBUG] Kakao API Error: {response.status_code} {response.text}")

        if response.status_code == 200:
            data = response.json()
            if data.get('documents'):
                # 도로명 주소 우선, 없으면 지번 주소
                doc = data['documents'][0]

                # 행정동 정보 추출
                if doc.get('address'):
                    addr = doc['address']
                    # 시/도, 시/군/구, 읍/면/동
                    region_1 = addr.get('region_1depth_name', '')  # 시/도
                    region_2 = addr.get('region_2depth_name', '')  # 시/군/구
                    region_3 = addr.get('region_3depth_name', '')  # 읍/면/동

                    result = f"{region_2} {region_3}" if region_3 else region_2
                    print(f"[DEBUG] Kakao Address Found: {result}")
                    return result

        print(f"[DEBUG] Kakao Address Not Found for {lat}, {lon}")
        return None
    except Exception as e:
        print(f"[ERROR] 카카오 API 주소 변환 실패: {e}")
        return None
