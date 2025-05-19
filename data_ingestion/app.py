from fastapi import FastAPI
import os
import json
import httpx
from datetime import datetime
import hashlib
import asyncio

app = FastAPI()

LANDING_ZONE = "/app/landing-zone"
DATA_FILE = os.path.join(LANDING_ZONE, "data.json")
HASH_FILE = os.path.join(LANDING_ZONE, "last_hash.txt")
DATABASE_API_URL = "http://database-api:5003/cars"
CHECK_INTERVAL = 10  # giây

# ✅ Tính hash để kiểm tra thay đổi
def calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# ✅ Kiểm tra file có thay đổi không
def has_file_changed(filepath: str, hashfile: str) -> bool:
    current_hash = calculate_file_hash(filepath)
    if os.path.exists(hashfile):
        with open(hashfile, 'r') as f:
            last_hash = f.read().strip()
        if current_hash == last_hash:
            return False  # Không thay đổi
    with open(hashfile, 'w') as f:
        f.write(current_hash)
    return True  # Có thay đổi

# ✅ Tách riêng hàm ingest logic
async def ingest_data_from_file():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("No data file found to ingest.")
    
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    ads = data.get("ads", [])
    if not ads:
        raise ValueError("No ads found in data file.")

    if not isinstance(ads, list):
        ads = [ads]

    for ad in ads:
        ad.setdefault("mileage", 0)
        ad.setdefault("created_at", datetime.utcnow().isoformat())
        ad.setdefault("shop_alias", "")
        ad.setdefault("images", [])
        ad.setdefault("videos", [])
        ad.setdefault("company_ad", False)

        if isinstance(ad.get("images"), list) and all(isinstance(img, str) for img in ad["images"]):
            ad["images"] = [{"image_url": img} for img in ad["images"]]

        if isinstance(ad["videos"], list) and all(isinstance(v, str) for v in ad["videos"]):
            ad["videos"] = [{"url": v} for v in ad["videos"]]

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(DATABASE_API_URL, json=ads)
        print(f">>> Response status code: {response.status_code}")
        response.raise_for_status()

    return {
        "status": "completed",
        "total_ads": len(ads),
        "inserted": len(ads)
    }

# ✅ Background task tự động ingest nếu file thay đổi
async def auto_ingest_loop():
    while True:
        try:
            if os.path.exists(DATA_FILE) and has_file_changed(DATA_FILE, HASH_FILE):
                print("[Auto Ingest] Detected change. Ingesting...",flush=True)
                result = await ingest_data_from_file()
                print(f"[Auto Ingest] Success: {result}",flush=True)
            else:
                print("[Auto Ingest] No changes detected.",flush=True)
        except Exception as e:
            print(f"[Auto Ingest Error] {e}",flush=True)
        await asyncio.sleep(CHECK_INTERVAL)

# ✅ Khởi chạy background task khi app start
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(auto_ingest_loop())

# ✅ Route kiểm tra hoạt động
@app.get("/")
def root():
    return {"message": "Data Ingestion Service is running"}

# ✅ Route ingest thủ công (gọi tay)
@app.get("/ingest")
async def ingest_data():
    try:
        result = await ingest_data_from_file()
        return result
    except httpx.HTTPStatusError as exc:
        return {"error": f"HTTP error {exc.response.status_code} - {exc.response.text}"}
    except httpx.ReadTimeout:
        print("[X] Lỗi: Server phản hồi quá chậm (ReadTimeout)")
        return {"error": "Timeout khi gửi dữ liệu tới Database API"}
    except Exception as e:
        return {"error": f"Failed to ingest data: {repr(e)}"}

