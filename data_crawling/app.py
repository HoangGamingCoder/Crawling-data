import logging
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.responses import HTMLResponse
from apscheduler.events import EVENT_JOB_ERROR
import requests
import json
import os
from datetime import datetime

app = FastAPI()
scheduler = BackgroundScheduler()

LANDING_ZONE = "landing-zone"
os.makedirs(LANDING_ZONE, exist_ok=True)
FILENAME = os.path.join(LANDING_ZONE, "data.json")

# Cấu hình logging
logfile = 'data_crawling.log'
logging.basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

URLS = [
    "https://gateway.chotot.com/v1/public/ad-listing-video?cg=2010&st=s%2Ck&source=listing&limit=10&page=1",
]

for page in range(2, 51):
    offset = (page - 1) * 20
    url = f"https://gateway.chotot.com/v1/public/ad-listing?cg=2010&o={offset}&page={page}&st=s,k&limit=20&fingerprint=79042857-57e5-4501-95b8-e84e0e0a40d6&include_expired_ads=true&key_param_included=true"
    URLS.append(url)

def crawl_data():
    all_ads = []
    seen_ids = set()

    headers = {"User-Agent": "Mozilla/5.0"}

    for idx, url in enumerate(URLS, start=1):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                ads = data.get("ads", [])
                new_ads = 0

                for ad in ads:
                    ad_id = ad.get("ad_id") or ad.get("list_id") or ad.get("id")
                    if ad_id and ad_id not in seen_ids:
                        seen_ids.add(ad_id)
                        all_ads.append(ad)
                        new_ads += 1

                logger.info(f"Trang {idx}: {len(ads)} tin, {new_ads} tin mới")
            else:
                logger.warning(f"Trang {idx}: Lỗi {response.status_code}")
        except Exception as e:
            logger.error(f"Trang {idx}: Lỗi {e}")

    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump({"ads": all_ads}, f, indent=2, ensure_ascii=False)

    logger.info(f"Lưu {len(all_ads)} tin vào {FILENAME}")

def job_error_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} gặp lỗi: {event.exception}")

scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)

scheduler.add_job(crawl_data, 'interval', hours=1, next_run_time=datetime.now())
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/")
def root():
    return {"message": "Data Crawler is running"}

@app.get("/crawl/manual")
def manual_crawl():
    crawl_data()
    return {"status": "Manual crawl completed"}

@app.get("/log", response_class=HTMLResponse)
def get_log():
    with open(logfile, 'r', encoding='utf-8') as f:
        content = f.read().replace('\n', '<br>')
    return f"""
    <html>
        <head>
            <title>Log Viewer</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body {{ font-family: monospace; white-space: pre-wrap; }}
            </style>
        </head>
        <body>{content}</body>
    </html>
    """

@app.get("/log/clear")
def clear_log():
    with open(logfile, 'w', encoding='utf-8') as f:
        pass
    return {"message": "Log cleared!"}