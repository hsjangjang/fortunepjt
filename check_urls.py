import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    "https://upload.wikimedia.org/wikipedia/commons/2/24/Blue_Tshirt.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Blue_Tshirt.jpg/400px-Blue_Tshirt.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/7/75/Blue_T-shirt.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Blue_T-shirt.jpg/400px-Blue_T-shirt.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/a/ac/Rain_jacket.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Rain_jacket.jpg/400px-Rain_jacket.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/98/Blue_Jeans.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Blue_Jeans.jpg/400px-Blue_Jeans.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/6e/Levis_501_jeans.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Levis_501_jeans.jpg/400px-Levis_501_jeans.jpg"
]

headers = {'User-Agent': 'Mozilla/5.0'}

print("Checking URLs...")
for url in urls:
    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req, context=ctx) as response:
            if response.status == 200:
                print(f"VALID: {url}")
    except Exception as e:
        pass
        # print(f"INVALID: {url} - {e}")
