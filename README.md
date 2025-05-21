
# 🚗 Chotot Car Crawler - Dự án Thu thập Dữ liệu Xe từ Chotot.com

Dự án này giúp tự động thu thập dữ liệu xe ô tô từ trang [chotot.com](https://www.chotot.com), lưu trữ vào cơ sở dữ liệu MySQL, đồng thời cung cấp giao diện web đơn giản để hiển thị dữ liệu. Hệ thống được container hóa bằng Docker để dễ triển khai và mở rộng.

---

## 📦 Cấu trúc thư mục chính

```
CRAWLING-DATA/
│
├── api-gateway/              # (Tuỳ chọn) Cổng API để truy cập dữ liệu tập trung
│   ├── Dockerfile            # Dockerfile cho api-gateway
│   ├── nginx.conf            # Cấu hình nginx cho api-gateway
│
├── data_crawling/            # Script crawl dữ liệu từ Chotot
│   ├── __pycache__/          # Cache Python
│   ├── app.py                # Script chính crawl dữ liệu
│   ├── data_crawling.log     # File log của quá trình crawl
│   ├── Dockerfile            # Dockerfile cho data_crawling
│   ├── requirements.txt      # Thư viện Python cho crawling
│   └── scheduler.py          # Script scheduler chạy crawl định kỳ
│
├── data_ingestion/           # Xử lý và lưu dữ liệu vào database
│   ├── app.py                # Script xử lý dữ liệu, đẩy vào DB
│   ├── Dockerfile            # Dockerfile cho data_ingestion
│   └── requirements.txt      # Thư viện Python cho ingestion
│
├── database-api/             # API truy vấn cơ sở dữ liệu
│   ├── app.py                # FastAPI app để query DB
│   ├── Dockerfile            # Dockerfile cho database-api
│   └── requirements.txt      # Thư viện cho database-api
│
├── init_db/
│   └── init.sql              # Script tạo bảng và dữ liệu mẫu cho MySQL
│
├── landing-zone/
│   ├── data.json             # Dữ liệu JSON tạm thời sau khi crawl
│   └── last_hash.txt         # Ghi hash dữ liệu cuối cùng để tránh trùng lặp
│
├── mysql_data/               # Volume dữ liệu MySQL (tự động tạo khi chạy container)
│
├── web-page/                 # Giao diện web hiển thị dữ liệu
│   ├── static/
│   │   └── style.css         # CSS cho giao diện
│   ├── templates/
│   │   └── index.html        # Giao diện HTML hiển thị dữ liệu
│   ├── app.py                # Flask web app
│   └── requirements.txt      # Thư viện cho Flask web-page
│
├── docker-compose.yml        # Cấu hình Docker Compose để chạy đa container
└── README.md                 # Hướng dẫn sử dụng dự án
```

---

## ⚙️ Công nghệ sử dụng

- **Python 3.10**
- **Requests** – Crawl dữ liệu
- **FastApi** – Giao diện web
- **MySQL** – Cơ sở dữ liệu lưu trữ
- **Docker, Docker Compose** – Triển khai

---

## 🚀 Cách sử dụng

### 1. Cài đặt Docker & Docker Compose

> Yêu cầu cài đặt: [Docker](https://www.docker.com/products/docker-desktop)

### 2. Build và chạy toàn bộ hệ thống

```bash
docker-compose up --build
```

Docker Compose sẽ tự động:
- Build image cho FastApi Web và service crawl
- Khởi tạo container MySQL, chạy `init.sql`
- Tạo dữ liệu trong MySQL
- Chạy giao diện web tại `http://127.0.0.1:5004`

---

## 🌐 Chi tiết các Dịch vụ & Endpoint

| **Dịch vụ**        | **URL kiểm tra**           | **Chức năng chính**                                                                 |
|--------------------|-----------------------------|--------------------------------------------------------------------------------------|
| **API Gateway**    | http://localhost/           | NGINX Reverse Proxy – chuyển tiếp yêu cầu đến các dịch vụ tương ứng.               |
| **Web Frontend**   | http://localhost/5004           | Giao diện người dùng để hiển thị danh sách tin đăng (sử dụng qua Gateway).         |
| **Crawling API**   | http://localhost:5001       | Thu thập dữ liệu từ Chợ Tốt và lưu vào thư mục `landing-zone` ở định dạng JSON.    |
| **Ingestion API**  | http://localhost:5002       | Đọc dữ liệu JSON từ `landing-zone` và gọi API để lưu vào cơ sở dữ liệu.            |
| **Database API**   | http://localhost:5003       | Cung cấp các RESTful API để đọc, ghi, truy vấn dữ liệu từ MySQL database.          |
| **Db_MySql**       | N/A (cổng 3309)             | MySQL DB dành cho lưu trữ dữ liệu..          |

---

## 🧩 Chi tiết từng dịch vụ

### 🔁 API Gateway (`api-gateway`)
- **URL:** `http://localhost/api/`
- **Mục tiêu:** Làm reverse proxy để định tuyến request:
  - `/data-crawling/*` → `data-crawling`
  - `/data-ingestion/*` → `data-ingestion`
  - `/database-api/*` → `database-api`
  - `/web-page` → `web-page`
- **Cấu hình:** Nằm trong file `api-gateway/nginx.conf`

---

### 💻 Web Frontend (`web-page`)
- **URL:** Truy cập qua `http://localhost:5004`
- **Chức năng:**
  - Giao diện người dùng hiển thị danh sách tin đăng xe.
  - Gọi API từ `database-api` để hiển thị dữ liệu từ MySQL.
  - Dùng  template engine như Jinja2.

---

### 🕷️ Crawling API (`data-crawling`)
- **URL:** `http://localhost:5001`
- **Chức năng:**
  - Thực hiện crawl dữ liệu tin đăng từ Chợ Tốt thông qua HTTP requests.
  - Lưu các tin đã crawl vào file `.json` trong thư mục `landing-zone`.
- **Ví dụ Endpoint:**
  - `GET /crawl/manual` → Bắt đầu crawl dữ liệu và lưu file.
  - `GET /log` → Trả về nội dung log (ghi lại quá trình crawl gần nhất).
  - `GET /log/clear` → Xóa nội dung log (reset lại log hiện tại để dễ theo dõi các lần crawl tiếp theo).

---

### 🔄 Ingestion API (`data-ingestion`)
- **URL:** `http://localhost:5002`
- **Chức năng:**
  - Đọc file JSON đã crawl ở `landing-zone`.
  - Gửi các bản ghi đến `database-api` để lưu vào MySQL.
- **Ví dụ Endpoint:**
  - `POST /ingest` → Thực hiện ingest toàn bộ file JSON vào DB.

---

### 🗃️ Database API (`database-api`)
- **URL:** `http://localhost:5003`
- **Chức năng:**
  - API CRUD cho dữ liệu quảng cáo xe hơi.
  - Tương tác trực tiếp với MySQL database (`db_mysql`).
- **Ví dụ Endpoint:**
    - `GET /cars` → Trả về danh sách tất cả các xe trong cơ sở dữ liệu.
    - `POST /cars` → Nhận dữ liệu mới từ ingestion để lưu vào DB.
    - `GET /cars/{id}` → Trả về chi tiết thông tin xe theo id.
    - `PUT /cars{id}` → Cập nhật thông tin xe theo id.
    - `DELETE /cars/{id}` → Xóa xe theo id.
    - `GET /cars/search` →  Tìm kiếm xe dựa trên các tham số truy vấn như model, brand, location, giá v.v.

---

## 🧪 Thao tác thủ công

### Crawl dữ liệu

```truy cập
http://127.0.0.1/api/data-crawling/crawl/manual (http://127.0.0.1:5001/crawl/manual)
```

### Ingest dữ liệu vào MySQL

```truy cập
http://127.0.0.1/api/data-ingestion/ingest (http://127.0.0.1:5002/ingest)
```

---

## 🛑 Dừng hệ thống

```bash
docker-compose down
```

---

## ✅ TODO

- [ ] Thêm bộ lọc dữ liệu theo khu vực/loại xe/tìm kiếm
- [ ] Lưu log crawl định kỳ
- [ ] Triển khai API Gateway

---