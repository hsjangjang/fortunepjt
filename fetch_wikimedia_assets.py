import os
import urllib.request
import json
import ssl
import time

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Target directory
output_dir = os.path.join('frontend', 'src', 'assets', 'images')
os.makedirs(output_dir, exist_ok=True)

# Search terms for each file
assets = {
    "top.png": "clothing sweater isolated",
    "bottom.png": "blue jeans isolated",
    "outer.png": "winter jacket isolated",
    "acc_scarf.png": "red scarf isolated",
    "acc_gloves.png": "leather gloves isolated",
    "acc_beanie.png": "beanie hat isolated",
    "accessories.png": "red scarf isolated", # Fallback
    "food_dish.png": "steak food",
    "food_dessert.png": "chocolate cake slice",
    "food_side.png": "kimchi bowl",
    "food_snack.png": "donut food"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_wikimedia_url(query):
    base_url = "https://commons.wikimedia.org/w/api.php"
    # Search for files
    search_params = f"?action=query&generator=search&gsrnamespace=6&gsrsearch=filetype:bitmap%20{query}&gsrlimit=1&prop=imageinfo&iiprop=url&format=json"
    try:
        req = urllib.request.Request(base_url + search_params.replace(" ", "%20"), headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                image_info = page_data.get('imageinfo', [])
                if image_info:
                    return image_info[0]['url']
    except Exception as e:
        print(f"Error searching for {query}: {e}")
    return None

print(f"Downloading images to {output_dir}...")

for filename, query in assets.items():
    print(f"Searching for '{query}' for {filename}...")
    image_url = get_wikimedia_url(query)
    
    if image_url:
        print(f"Found URL: {image_url}")
        filepath = os.path.join(output_dir, filename)
        try:
            req = urllib.request.Request(image_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as response, open(filepath, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
                print(f"SUCCESS: {filename} ({len(data)} bytes)")
        except Exception as e:
            print(f"FAILED to download {filename}: {e}")
    else:
        print(f"NOT FOUND: No image found for '{query}'")
    
    time.sleep(1) # Be polite to the API

print("Download complete.")
