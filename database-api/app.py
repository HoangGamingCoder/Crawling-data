from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import mysql.connector
import os
from typing import List, Optional
from datetime import datetime
from fastapi.encoders import jsonable_encoder

# Cấu hình kết nối MySQL từ môi trường
db_config = {
    'host': os.getenv('MYSQL_HOST', 'db'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DB', 'oto_ads')
}

app = FastAPI()

# Kết nối MySQL
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Models
class CarImage(BaseModel):
    image_url: str

class CarVideo(BaseModel):
    id: str
    thumbnail: Optional[str] = None
    url: Optional[str] = None
    gif_url: Optional[str] = None

class Car(BaseModel):
    ad_id: int
    list_id: int
    list_time: int
    state: Optional[str] = None
    type: Optional[str] = None
    account_name: Optional[str] = None
    region: Optional[int] = None
    category: Optional[int] = None
    company_ad: Optional[bool] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    price: Optional[int] = None
    image: Optional[str] = None
    account_id: Optional[int] = None
    shop_alias: Optional[str] = None
    status: Optional[str] = None
    carbrand: Optional[int] = None
    carmodel: Optional[int] = None
    carorigin: Optional[int] = None
    carseats: Optional[int] = None  # <-- sửa ở đây
    fuel: Optional[int] = None
    gearbox: Optional[int] = None
    mfdate: Optional[int] = None
    mileage: Optional[float] = None
    mileage_v2: Optional[float] = None
    area: Optional[int] = None
    condition_ad: Optional[int] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    contain_videos: Optional[int] = None
    created_at: Optional[datetime] = None
    images: Optional[List[CarImage]] = []
    videos: Optional[List[CarVideo]] = []

# API lấy danh sách ads
@app.get("/cars")
def get_cars():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM ads')
    ads = cursor.fetchall()
    conn.close()
    return ads

@app.get("/cars/search")
def search_cars(
    search_value: str,
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    sort: Optional[str] = Query(None, regex="^(price-asc|price-desc)?$"),
    region: Optional[int] = None,
):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ads")
        all_cars = cursor.fetchall()

        # Lọc theo từ khóa
        filtered = [
            car for car in all_cars
            if search_value.lower() in (car.get("subject") or "").lower()
        ]

        # Lọc theo region nếu có
        if region is not None:
            filtered = [car for car in filtered if str(car.get("region")) == str(region)]

        # Sắp xếp
        if sort == "price-desc":
            filtered.sort(key=lambda x: x.get("price") or 0, reverse=True)
        elif sort == "price-asc":
            filtered.sort(key=lambda x: x.get("price") or 0)

        # Phân trang
        start = (page - 1) * limit
        end = start + limit
        paginated = filtered[start:end]

        return {
            "data": paginated,
            "total": len(filtered),
            "page": page,
            "limit": limit,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# API thêm ads
@app.post("/cars")
def add_cars(cars: List[Car] = Body(...)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM ad_images")
            cursor.execute("DELETE FROM ad_videos")
            cursor.execute("DELETE FROM ads")

            sql = """
                INSERT INTO ads (
                    ad_id, list_id, list_time, state, type, account_name,
                    region, category, company_ad, subject, body, price,
                    image, account_id, shop_alias, status, carbrand, carmodel,
                    carorigin, carseats, fuel, gearbox, mfdate, mileage,mileage_v2, area,
                    condition_ad, longitude, latitude, contain_videos, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """
            values = []
            for car in cars:
                values.append((
                    car.ad_id,
                    car.list_id,
                    car.list_time,
                    car.state,
                    car.type,
                    car.account_name,
                    car.region,
                    car.category,
                    int(car.company_ad) if car.company_ad is not None else None,
                    car.subject,
                    car.body,
                    car.price,
                    car.image,
                    car.account_id,
                    car.shop_alias,
                    car.status,
                    car.carbrand,
                    car.carmodel,
                    car.carorigin,
                    car.carseats,
                    car.fuel,
                    car.gearbox,
                    car.mfdate,
                    car.mileage,
                    car.mileage_v2,
                    car.area,
                    car.condition_ad,
                    car.longitude,
                    car.latitude,
                    int(car.contain_videos) if car.contain_videos is not None else None,
                    car.created_at.strftime("%Y-%m-%d %H:%M:%S") if car.created_at else None
                ))
            
            cursor.executemany(sql, values)

            # Nếu có hình ảnh và video, bạn phải xử lý riêng vì có bảng riêng
            
            # Ví dụ: lưu từng ảnh
            for car in cars:
                for img in car.images:
                    cursor.execute(
                        "INSERT INTO ad_images (ad_id, image_url) VALUES (%s, %s)",
                        (car.ad_id, img.image_url)
                    )
            
            # Lưu từng video
            for car in cars:
                for vid in car.videos:
                    cursor.execute(
                        "INSERT INTO ad_videos (id, ad_id, thumbnail, url, gif_url) VALUES (%s, %s, %s, %s, %s)",
                        (vid.id, car.ad_id, vid.thumbnail, vid.url, vid.gif_url)
                    )

        conn.commit()
        return {"message": f"{len(cars)} car ads inserted successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
   

# API cập nhật car ad
@app.put("/cars/{id}")
def update_car(id: int, car: Car):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE ads SET subject = %s, body = %s, price = %s WHERE ad_id = %s",
                (car.subject, car.body, car.price, id)
            )
        conn.commit()
        return {"message": "Car ad updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# API xóa car ad
@app.delete("/cars/{id}")
def delete_car(id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM ad_images WHERE ad_id = %s", (id,))
            cursor.execute("DELETE FROM ad_videos WHERE ad_id = %s", (id,))
            cursor.execute("DELETE FROM ads WHERE ad_id = %s", (id,))
        conn.commit()
        return {"message": "Car ad deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
