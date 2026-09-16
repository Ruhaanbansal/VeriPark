import os
import urllib.request
import urllib.parse
import json

TARGET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "public", "images", "lots")
os.makedirs(TARGET_DIR, exist_ok=True)

queries = {
    "lot-metro-hub": "multi-storey car park railway station",
    "lot-commercial-tower": "commercial office building multi-storey car park",
    "lot-civic-center": "underground parking garage",
    "lot-indiranagar": "automated parking system mechanical",
    "lot-hospital": "hospital parking garage building",
    "lot-koramangala": "shopping mall multi-storey car park",
    "lot-express-deck": "multi-level car parking deck structure"
}

headers = {
    "User-Agent": "VeriParkScraper/1.0 (faithpark@veripark.app)"
}

print(f"Target directory: {TARGET_DIR}")

for key, query in queries.items():
    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
        f"&gsrsearch={urllib.parse.quote(query)}"
        f"&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url|mime|size&format=json"
    )
    req = urllib.request.Request(api_url, headers=headers)
    found = False
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                info = page.get("imageinfo", [{}])[0]
                img_url = info.get("url")
                mime = info.get("mime", "")
                size = info.get("size", 0)
                # Keep file size reasonable (< 2MB)
                if img_url and ("image/jpeg" in mime or "image/png" in mime) and size < 5000000:
                    print(f"Downloading {key} from {img_url} ({size} bytes)...")
                    # Download both .jpg and .svg (or whatever mock data references)
                    img_req = urllib.request.Request(img_url, headers=headers)
                    with urllib.request.urlopen(img_req) as img_resp:
                        img_bytes = img_resp.read()
                    
                    # Save as jpg
                    jpg_path = os.path.join(TARGET_DIR, f"{key}.jpg")
                    with open(jpg_path, "wb") as f:
                        f.write(img_bytes)
                    print(f"Saved {jpg_path}")
                    found = True
                    break
    except Exception as e:
        print(f"Error fetching {query}: {e}")

    if not found:
        print(f"Warning: Could not find image for {key}")
