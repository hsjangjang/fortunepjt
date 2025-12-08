"""
75개 음식 이미지 다운로드 스크립트
"""
import os
import urllib.request
import time

save_dir = r'c:\Users\99gkt\OneDrive\바탕 화면\pjt\frontend\src\assets\images\food'
os.makedirs(save_dir, exist_ok=True)

# 75개 음식 이미지 URL
foods = {
    # 한식 찌개/탕 (1-15)
    'kimchi_jjigae': 'https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=400',
    'doenjang_jjigae': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'sundubu_jjigae': 'https://images.unsplash.com/photo-1583224964978-2257b960c3d3?w=400',
    'galbitang': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'samgyetang': 'https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=400',
    'budae_jjigae': 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=400',
    'gamjatang': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'yukgaejang': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'tteokguk': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'eomuk_tang': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'sogogi_gukbap': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'dwaeji_gukbap': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'seolleongtang': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'gomtang': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',
    'haejangguk': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=400',

    # 한식 고기 (16-24)
    'samgyeopsal': 'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=400',
    'bulgogi': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400',
    'galbi_jjim': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400',
    'jeyuk_bokkeum': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400',
    'dakgalbi': 'https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=400',
    'jokbal': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400',
    'bossam': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400',
    'gopchang': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400',
    'makchang': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400',

    # 한식 밥/비빔 (25-30)
    'bibimbap': 'https://images.unsplash.com/photo-1553163147-622ab57be1c7?w=400',
    'gimbap': 'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=400',
    'japchae': 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=400',
    'bokkeumbap': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400',
    'kimchi_bokkeumbap': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400',
    'jumeokbap': 'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=400',

    # 분식 (31-37)
    'tteokbokki': 'https://images.unsplash.com/photo-1635363638580-c2809d049eee?w=400',
    'sundae': 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=400',
    'ramyeon': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',
    'mandu': 'https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=400',
    'twigim': 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=400',
    'haemul_pajeon': 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=400',
    'kimchi_jeon': 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=400',

    # 면류 (38-48)
    'naengmyeon': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',
    'kalguksu': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',
    'janchi_guksu': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',
    'jajangmyeon': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',
    'jjamppong': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',
    'bokkeummyeon': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',
    'udon': 'https://images.unsplash.com/photo-1618841557871-b4664fbf0cb3?w=400',
    'ramen': 'https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=400',
    'ssalguksu': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=400',
    'pad_thai': 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=400',
    'bokkeum_udon': 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400',

    # 중식 (49-50)
    'tangsuyuk': 'https://images.unsplash.com/photo-1525755662778-989d0524087e?w=400',
    'mapo_tofu': 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=400',

    # 일식 (51-55)
    'sushi': 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400',
    'sashimi': 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400',
    'donkatsu': 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400',
    'curry': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400',
    'omurice': 'https://images.unsplash.com/photo-1525755662778-989d0524087e?w=400',

    # 양식 (56-63)
    'steak': 'https://images.unsplash.com/photo-1600891964092-4316c288032e?w=400',
    'pasta': 'https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=400',
    'pizza': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400',
    'hamburger': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400',
    'salad': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
    'soup': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400',
    'risotto': 'https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=400',
    'omelette': 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=400',

    # 치킨 (64-69)
    'fried_chicken': 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400',
    'yangnyeom_chicken': 'https://images.unsplash.com/photo-1575932444877-5106bee2a599?w=400',
    'ganjang_chicken': 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400',
    'chicken_nuggets': 'https://images.unsplash.com/photo-1562967914-608f82629710?w=400',
    'dakgangjeong': 'https://images.unsplash.com/photo-1575932444877-5106bee2a599?w=400',
    'jjimdak': 'https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=400',

    # 디저트/음료 (70-75)
    'ice_cream': 'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=400',
    'patbingsu': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400',
    'cake': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400',
    'waffle': 'https://images.unsplash.com/photo-1562376552-0d160a2f238d?w=400',
    'americano': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400',
    'cafe_latte': 'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400',
}

print(f'Downloading {len(foods)} images to {save_dir}')
count = 0
failed = []

for name, url in foods.items():
    try:
        filepath = os.path.join(save_dir, f'{name}.png')
        urllib.request.urlretrieve(url, filepath)
        count += 1
        print(f'[{count}/{len(foods)}] {name}')
        time.sleep(0.2)
    except Exception as e:
        failed.append(name)
        print(f'[FAIL] {name}: {e}')

print(f'\nComplete! Downloaded {count}/{len(foods)} images')
if failed:
    print(f'Failed: {failed}')
