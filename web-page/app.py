from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATABASE_API_URL = "http://database-api:5003/cars"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/cars")
async def get_all_cars(
    page: int = Query(1),
    limit: int = Query(10),
    sort: str = Query(""),
    region: Optional[List[str]] = Query(None)
):
    try:
        response = requests.get(DATABASE_API_URL)
        response.raise_for_status()
        all_cars = response.json()

        if region:
            all_cars = [car for car in all_cars if str(car.get("region")) in region]

        if sort == "price-desc":
            all_cars.sort(key=lambda x: x.get("price", 0))
        elif sort == "price-asc":
            all_cars.sort(key=lambda x: x.get("price", 0), reverse=True)

        start = (page - 1) * limit
        end = start + limit
        paginated = all_cars[start:end]

        return {
            "data": paginated,
            "total": len(all_cars),
            "page": page,
            "limit": limit,
        }
    except requests.RequestException as e:
        return JSONResponse(content={"error": f"Lỗi kết nối đến database-api: {str(e)}"}, status_code=500)

@app.get("/cars/{search_value}")
async def search_cars(
    search_value: str,
    page: int = Query(1),
    limit: int = Query(10),
    sort: str = Query(""),
    region: Optional[str] = Query(None)
):
    try:
        params = {
            "search_value": search_value,
            "page": page,
            "limit": limit,
            "sort": sort,
        }
        if region:
            params["region"] = region

        response = requests.get(f"{DATABASE_API_URL}/search", params=params)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        return JSONResponse(content={"error": f"Lỗi kết nối đến database-api: {str(e)}"}, status_code=500)
