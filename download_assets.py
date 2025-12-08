import os
import urllib.request
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Target directory
output_dir = os.path.join('frontend', 'src', 'assets', 'images')
os.makedirs(output_dir, exist_ok=True)

# Image mappings (Filename -> URL)
images = {
    # OOTD Assets - Verified Wikimedia Thumbnails
    "top.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Sweater_-_f.jpg/320px-Sweater_-_f.jpg", # Trying 320px
    "bottom.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Tube_top_and_blue_jeans_crop.jpg/400px-Tube_top_and_blue_jeans_crop.jpg",
    "outer.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Windbreaker_Jacket%2C_Hood_Outside_Transparency.png/400px-Windbreaker_Jacket%2C_Hood_Outside_Transparency.png",
    
    # Specific Accessories - Verified
    "acc_scarf.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Red_scarf.jpg/400px-Red_scarf.jpg",
    "acc_gloves.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Pair_of_leather_gloves.jpg/400px-Pair_of_leather_gloves.jpg",
    "acc_beanie.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Beanie.svg/400px-Beanie.svg.png",
    "accessories.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Red_scarf.jpg/400px-Red_scarf.jpg", # Fallback for generic
    
    # Menu Assets - Verified
    "food_dish.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Steak.jpg/400px-Steak.jpg",
    "food_dessert.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Chocolate_cake.jpg/400px-Chocolate_cake.jpg",
    "food_side.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Korean_Gimchi01.jpg/400px-Korean_Gimchi01.jpg",
    "food_snack.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Kkwabaegi.jpg/400px-Kkwabaegi.jpg"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Downloading images to {output_dir}...")

for filename, url in images.items():
    filepath = os.path.join(output_dir, filename)
    try:
        print(f"Downloading {filename} from {url}...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response, open(filepath, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            print(f"SUCCESS: {filename} ({len(data)} bytes)")
    except Exception as e:
        print(f"FAILED: {filename} - {e}")
        # Fallback to LoremFlickr (Safe Keywords)
        try:
            print(f"Retrying {filename} with LoremFlickr...")
            fallback_url = f"https://loremflickr.com/400/400/clothing,texture/all"
            if "food" in filename:
                fallback_url = f"https://loremflickr.com/400/400/food,meal/all"
            
            req = urllib.request.Request(fallback_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as response, open(filepath, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
                print(f"SUCCESS (Fallback): {filename} ({len(data)} bytes)")
        except Exception as e2:
            print(f"FATAL: Could not download {filename} - {e2}")

print("Download complete.")
