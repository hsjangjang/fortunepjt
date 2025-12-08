"""
마지막 2개 OOTD 의류 이미지 다운로드
"""
import os
import urllib.request
import time

save_dir = r'c:\Users\99gkt\OneDrive\바탕 화면\pjt\frontend\src\assets\images\ootd'

# 마지막 실패한 2개
clothes = {
    'bottom_slacks': 'https://pngimg.com/uploads/suit/small/suit_PNG8137.png',  # 슬랙스 (정장 바지)
    'outer_blazer': 'https://pngimg.com/uploads/suit/small/suit_PNG8118.png',  # 블레이저 (정장 자켓)
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f'Downloading final 2 images to {save_dir}')

for name, url in clothes.items():
    try:
        filepath = os.path.join(save_dir, f'{name}.png')
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        print(f'[OK] {name}')
        time.sleep(0.3)
    except Exception as e:
        print(f'[FAIL] {name}: {e}')

print('Done!')
