from flask import Flask, render_template, jsonify, request
import requests
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Đường dẫn API backend
DATABASE_API_URL = os.getenv("DATABASE_API_URL", "http://database-api:5003/cars")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cars", methods=["GET"])
def get_all_cars():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "")
    regions = request.args.getlist("region")

    try:
        response = requests.get(DATABASE_API_URL)
        response.raise_for_status()
        all_cars = response.json()

        if regions:
            all_cars = [car for car in all_cars if str(car.get("region")) in regions]

        if sort == "price-desc":
            all_cars.sort(key=lambda x: x.get("price", 0))
        elif sort == "price-asc":
            all_cars.sort(key=lambda x: x.get("price", 0), reverse=True)

        start = (page - 1) * limit
        end = start + limit
        paginated = all_cars[start:end]

        return jsonify({
            "data": paginated,
            "total": len(all_cars),
            "page": page,
            "limit": limit,
        })
    except requests.RequestException as e:
        return jsonify({"error": f"Lỗi kết nối đến database-api: {str(e)}"}), 500

@app.route("/cars/<search_value>", methods=["GET"])
def search_cars(search_value):
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "")
    region = request.args.get("region", None)

    try:
        response = requests.get(DATABASE_API_URL)
        response.raise_for_status()
        all_cars = response.json()

        # Lọc theo từ khóa trong subject
        filtered = [
            car for car in all_cars
            if search_value.lower() in (car.get("subject") or "").lower()
        ]

        # Lọc theo region nếu có
        if region:
            filtered = [car for car in filtered if str(car.get("region")) == str(region)]

        # Sắp xếp
        if sort == "price-desc":
            filtered.sort(key=lambda x: x.get("price", 0))
        elif sort == "price-asc":
            filtered.sort(key=lambda x: x.get("price", 0), reverse=True)

        # Phân trang
        start = (page - 1) * limit
        end = start + limit
        paginated = filtered[start:end]

        return jsonify({
            "data": paginated,
            "total": len(filtered),
            "page": page,
            "limit": limit,
        })

    except requests.RequestException as e:
        return jsonify({"error": f"Lỗi kết nối đến database-api: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5004)
