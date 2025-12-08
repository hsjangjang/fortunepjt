"""
50개 OOTD 의류 이미지 다운로드 - pngimg.com에서 의류 제품 PNG (수정판)
"""
import os
import urllib.request
import time

save_dir = r'c:\Users\99gkt\OneDrive\바탕 화면\pjt\frontend\src\assets\images\ootd'
os.makedirs(save_dir, exist_ok=True)

# 실패한 27개 이미지만 다시 다운로드
clothes = {
    # 상의
    'top_tshirt': 'https://pngimg.com/uploads/tshirt/small/tshirt_PNG5451.png',  # 반팔 티셔츠 (검정)
    'top_longsleeve': 'https://pngimg.com/uploads/tshirt/small/tshirt_PNG5453.png',  # 긴팔 티
    'top_thin_knit': 'https://pngimg.com/uploads/sweater/small/sweater_PNG10.png',  # 얇은 니트
    'top_knit': 'https://pngimg.com/uploads/sweater/small/sweater_PNG20.png',  # 니트
    'top_thick_knit': 'https://pngimg.com/uploads/sweater/small/sweater_PNG30.png',  # 두꺼운 니트
    'top_turtleneck': 'https://pngimg.com/uploads/sweater/small/sweater_PNG40.png',  # 터틀넥
    'top_polo': 'https://pngimg.com/uploads/polo_shirt/small/polo_shirt_PNG8173.png',  # 폴로

    # 하의
    'bottom_shorts': 'https://pngimg.com/uploads/jeans/small/jeans_PNG5755.png',  # 반바지 (진 쇼츠)
    'bottom_linen': 'https://pngimg.com/uploads/jeans/small/jeans_PNG5756.png',  # 린넨 팬츠
    'bottom_cotton': 'https://pngimg.com/uploads/jeans/small/jeans_PNG5758.png',  # 면바지
    'bottom_slacks': 'https://pngimg.com/uploads/suit/small/suit_PNG8333.png',  # 슬랙스
    'bottom_jogger': 'https://pngimg.com/uploads/leggings/small/leggings_PNG10.png',  # 조거팬츠
    'bottom_fleece': 'https://pngimg.com/uploads/leggings/small/leggings_PNG20.png',  # 기모 바지
    'bottom_corduroy': 'https://pngimg.com/uploads/jeans/small/jeans_PNG5759.png',  # 코듀로이
    'bottom_wool': 'https://pngimg.com/uploads/jeans/small/jeans_PNG5760.png',  # 울 팬츠
    'bottom_leggings': 'https://pngimg.com/uploads/leggings/small/leggings_PNG1.png',  # 레깅스
    'bottom_skirt': 'https://pngimg.com/uploads/dress/small/dress_PNG100.png',  # 치마
    'bottom_longskirt': 'https://pngimg.com/uploads/dress/small/dress_PNG110.png',  # 롱스커트
    'bottom_fleece_leggings': 'https://pngimg.com/uploads/leggings/small/leggings_PNG30.png',  # 기모 레깅스
    'bottom_wide': 'https://pngimg.com/uploads/jeans/small/jeans_PNG5761.png',  # 와이드 팬츠
    'bottom_cargo': 'https://pngimg.com/uploads/jeans/small/jeans_PNG5762.png',  # 카고 팬츠

    # 아우터
    'outer_cardigan': 'https://pngimg.com/uploads/sweater/small/sweater_PNG50.png',  # 가디건
    'outer_blazer': 'https://pngimg.com/uploads/suit/small/suit_PNG8330.png',  # 블레이저

    # 액세서리
    'acc_scarf': 'https://pngimg.com/uploads/scarf/small/scarf_PNG1.png',  # 머플러
    'acc_gloves': 'https://pngimg.com/uploads/gloves/small/gloves_PNG8269.png',  # 장갑
    'acc_beanie': 'https://pngimg.com/uploads/hat/small/hat_PNG5703.png',  # 비니 (모자 카테고리)
    'acc_cap': 'https://pngimg.com/uploads/cap/small/cap_PNG5688.png',  # 모자
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f'Downloading {len(clothes)} failed OOTD images to {save_dir}')
count = 0
failed = []

for name, url in clothes.items():
    try:
        filepath = os.path.join(save_dir, f'{name}.png')
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        count += 1
        print(f'[{count}/{len(clothes)}] {name}')
        time.sleep(0.3)
    except Exception as e:
        failed.append((name, str(e)))
        print(f'[FAIL] {name}: {e}')

print(f'\nComplete! Downloaded {count}/{len(clothes)} images')
if failed:
    print(f'Failed ({len(failed)}):')
    for name, err in failed:
        print(f'  - {name}: {err}')
